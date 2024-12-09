from typing import Dict, List, Optional, Any
import chainlit as cl
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import re
from llm_wrapper import create_llm, BaseLLMWrapper
from doc_formatter import DocFormatter
import os
from datetime import datetime

PART_LENGTH = 1000
# 定义提示模板
OUTLINE_TEMPLATE = """
基于以下主题和摘要生成一个详细的报告大纲，并为每个部分标注预期字数。
总字数要求：{total_words}字

主题：{title}
摘要：{summary}

请按以下格式输出：
1. 第一部分标题 (预期字数)
    1.1 子部分标题 (预期字数)
    1.2 子部分标题 (预期字数)
    ...
2. 第二部分标题 (预期字数)
    2.1 子部分标题 (预期字数)
    2.2 子部分标题 (预期字数)
    ...
...

注意：所有部分的字数总和应该接近要求的总字数。
"""

# Add new template for summary
SUMMARY_TEMPLATE = """
请基于以下主题生成一段简洁的摘要，概括报告的主要内容和目的：

主题：{title}

要求：
1. 控制在200字以内
2. 清晰概括主要内容
3. 突出报告价值和意义
"""

CONTENT_SUMMARY_TEMPLATE = """
请对以下内容进行概括总结，用100字左右简要说明主要内容：

{content}

请生成概要：
"""
# 添加新的数据结构来表示大纲节点
class OutlineNode:
    def __init__(self, title: str, words: int, number: Optional[str] = None):
        self.title = title
        self.words = words
        self.number = number
        self.content = ""
        self.children = []
        self.level = 1  # 默认为一级标题
    
    def add_child(self, node: 'OutlineNode') -> None:
        self.children.append(node)
    
    def is_leaf(self) -> bool:
        return len(self.children) == 0
    
    def __repr__(self) -> str:
        return f"OutlineNode(title='{self.title}', words={self.words}, number='{self.number}', level={self.level})"
    
    def to_text(self, include_words: bool = True, indent: str = "") -> str:
        """将节点及其子节点转换为文本形式
        
        Args:
            include_words: 是否包含字数信息
            indent: 缩进字符串，用于递归调用
        """
        # 构建当前节点的文本
        if include_words:
            node_text = f"{indent}{self.number or ''} {self.title} ({self.words}字)"
        else:
            node_text = f"{indent}{self.number or ''} {self.title}"
        
        # 如果有子节点，递归处理
        if self.children:
            child_texts = [
                child.to_text(include_words, indent + "    ")
                for child in self.children
            ]
            return node_text + "\n" + "\n".join(child_texts)
        
        return node_text
    
    def to_simple_text(self) -> str:
        """转换为简单的文本形式（用于提示模板）"""
        return self.to_text(include_words=True, indent="- ")


def parse_outline(outline_text: str, root_title: str = "报告正文") -> OutlineNode:
    """将大纲文本解析为树形结构"""
    print(f"[DEBUG] Parsing outline text:\n{outline_text}")
    lines = outline_text.strip().split('\n')
    root = OutlineNode(root_title, 0)  # 创建根节点
    current_nodes = [root]  # 用于跟踪当前每个层级的节点

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 使用正则表达式匹配编号、标题和字数
        match = re.search(r'(\d+[\.\d+]*)\s*(.+?)\s*\((\d+)字\)', line)
        if match:
            number, title, words = match.groups()
            number = number.strip(".")
            indent_level = len(number.split("."))  # 1.,1.1 计算被.分割的数量,删掉空元素
            print(f"[DEBUG] number: {number}, title: {title}, words: {words}, indent_level: {indent_level}")

            node = OutlineNode(
                title=title.strip(),
                words=int(words),
                number=number
            )
            node.level = indent_level  # 设置节点层级（一级标题为1级）

            current_nodes.append(node)


            # 添加为上一级节点的子节点
            if indent_level > 1:
                # 找到前缀一致的父节点
                parent_number = '.'.join(number.split('.')[:-1])  # 获取父节点的编号
                print(f"[DEBUG] parent_number: {parent_number}")
                parent = next((n for n in current_nodes if n.number == parent_number), None)
                if parent:
                    parent.add_child(node)  # 确保子节点被添加
            else:
                root.add_child(node)

    print(f"[DEBUG] Parsed outline tree: {root}")
    return root

class ReportGenerator:
    def __init__(self, llm_backend: str = "openai", model_config: Optional[Dict[str, Any]] = None):
        print(f"[DEBUG] Initializing ReportGenerator with backend: {llm_backend}")
        self.llm = create_llm(backend=llm_backend, model_config=model_config).get_model()
        self.title = ""
        self.overview = ""
        self.total_words = 0
        self.outline_root = None  # 存储大纲树的根节点
        self.current_node = None  # 当前正在处理的节点
        self.summary = ""  # Add new field for summary
        self.sections_content = []  # 用于存储每个部分的内容
        self.current_part_content = []  # 存储当前部分已生成的内容
        
    
    async def generate_content_dfs(self, node: OutlineNode) -> str:
        """深度优先遍历生成内容"""
        # 如果有子节点，先生成所有子节点的内容
        if not node.is_leaf():
            all_content = []
            for child in node.children:
                child_content = await self.generate_content_dfs(child)
                all_content.append(child_content)
            
            # 合并所有子节点的内容
            node.content = "\n\n".join(all_content)
            return node.content
        
        # 对于叶子节点，使用分段生成方法
        print(f"[DEBUG] Generating content for leaf node: {node.title}")
        await cl.Message(content=f"正在生成：{node.title}...").send()
        
        content = await self.generate_section_content(node)
        
        node.content = content
        return content
    
    def count_chinese_chars(self, text: str) -> int:
        """统计中文字符数"""
        return len(re.findall(r'[\u4e00-\u9fff]', text))

    def export_to_word(self) -> str:
        """修改导出方法以支持树形结构"""
        formatter = DocFormatter()
        
        # 添加标题
        formatter.add_title(self.title)
        
        # 添加摘要
        formatter.add_chapter("摘要")
        formatter.add_content(self.summary)
        
        # 使用深度优先遍历添加正文内容
        def add_node_content(node: OutlineNode):
            # 如果不是叶子节点，
            if node.level == 1 and node.number and node.title:
                formatter.add_chapter(f"{node.number} {node.title}")
            elif node.level == 2 and node.number and node.title:
                formatter.add_section(f"{node.number} {node.title}")
            elif node.level == 3 and node.number and node.title:
                formatter.add_subsection(f"{node.number} {node.title}")
            if node.is_leaf() and node.content:
                formatter.add_content(node.content)
            
            for child in node.children:
                add_node_content(child)
        
        # 从根节点开始添加内容
        for node in self.outline_root.children:
            add_node_content(node)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.docx"
        
        # 确保 output 目录存在
        os.makedirs("output", exist_ok=True)
        filepath = os.path.join("output", filename)
        
        # 保存文档
        formatter.save(filepath)
        return filepath,filename

    async def generate_content_summary(self, content: str) -> str:
        """生成内容概要"""
        summary_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template=CONTENT_SUMMARY_TEMPLATE,
                input_variables=["content"]
            )
        )
        
        return await cl.make_async(summary_chain.run)(
            content=content
        )
    
    async def generate_section_content(self, node: OutlineNode) -> str:
        """分段生成章节内容，使用递归的方式处理大段落"""
        total_words = node.words
        
        if total_words <= PART_LENGTH:
            # 如果字数在限制范围内，直接生成内容
            return await self._generate_single_part(node)
        
        # 为大段落生成子大纲
        subsection_outline = await self._generate_subsection_outline({
            "title": node.title,
            "words": node.words
        })
        
        # 存储所有生成的内容
        all_content = []
        
        # 遍历大纲树生成内容
        async def traverse_outline(node: OutlineNode) -> str:
            if node.is_leaf():  # 如果是叶子节点
                return await self._generate_single_part(node)
            
            all_content = []
            for child in node.children:
                content = await traverse_outline(child)
                all_content.append(content)
                
                # 显示生成进度
                actual_words = self.count_chinese_chars(content)
                await cl.Message(
                    content=f"完成子部分：{child.title}\n字数：{actual_words}").send()
            
            return "\n".join(all_content)

        # 从根节点开始遍历
        all_content = await traverse_outline(subsection_outline)
        
        return "\n".join(all_content)

    async def _generate_subsection_outline(self, section: Dict[str, Any]) -> OutlineNode:
        """生成子部分大纲"""

        SUBSECTION_OUTLINE_TEMPLATE = """
请为当前部分生成详细的子大纲，并为每个子部分标注预期字数：

主题：{title}
全局大纲概述：
{full_outline}
当前部分标题：{section_title}
总字数要求：{target_words}字

要求：
1. 仅根据当前部分{section_title}生成子部分大纲，确保与全局大纲保持一致，但不直接引用全局大纲内容。
2. 将当前部分{section_title}的内容分成多个子部分，每个子部分不超过{max_length}字。
3. 子部分之间要有逻辑连贯性和自然过渡。
4. 按以下格式输出：
    1. 子部分标题 (字数)
    2. 子部分标题 (字数)
    ...
5. 请勿输出其他部分的大纲或与当前部分无关的信息。

现在，请开始生成 {section_title} 的子部分大纲：
"""

        outline_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template=SUBSECTION_OUTLINE_TEMPLATE,
                input_variables=["title", "section_title", "target_words", "max_length"]
            )
        )
        
        outline_text = await cl.make_async(outline_chain.run)(
            title=self.title,
            full_outline=self.outline_root.to_simple_text(),
            section_title=section["title"],
            target_words=section["words"],
            max_length=PART_LENGTH
        )
        
        return parse_outline(outline_text, section["title"])

    async def _generate_single_part(self, node: OutlineNode, subsection_outline: OutlineNode = None) -> str:
        """生成单个部分的内容"""
        SINGLE_PART_TEMPLATE = """
        请基于以下信息生成内容：
        
        报告主题：{title}
        报告概述：{overview}
        当前部分：{section_title}
        目标字数：{target_words}字
        当前层级：{level}级标题
        
        全文大纲：
        {full_outline}
        
        {section_outline}
        
        要求：
        1. 内容要详实、专业、有深度
        2. 控制在目标字数范围内
        3. 行文流畅自然，注意与整体结构的连贯性
        4. 如果提供了当前节大纲，需要严格按照大纲展开
        
        请直接生成内容：
        """
        
        section_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template=SINGLE_PART_TEMPLATE,
                input_variables=[
                    "title", "overview", "section_title", 
                    "target_words", "level", "full_outline", "section_outline"
                ]
            )
        )
        
        # 将完整大纲转换为文本形式
        full_outline = self.outline_root.to_text(include_words=True)
        
        # 如果节点有子节点，生成当前节的子大纲
        section_outline_text = ""
        if subsection_outline:
            section_outline_text = "当前节大纲：\n" + subsection_outline.to_text(include_words=True)
        
        content = await cl.make_async(section_chain.run)(
            title=self.title,
            overview=self.overview,
            section_title=node.title,
            target_words=node.words,
            level=node.level,
            full_outline=full_outline,
            section_outline=section_outline_text
        )
        
        return content

@cl.on_chat_start
async def start():
    model_config = {
        "temperature": 0.7,
        # 其他配置参数...
    }
    
    generator = ReportGenerator(
        llm_backend="openai",  # 或 "ollama"
        model_config=model_config
    )
    cl.user_session.set("generator", generator)
    
    # 发送欢迎消息
    await cl.Message(
        content="你好！我是AI写作助手。请按以下格式输入报告需求：\n"
                "主题：你的报告主题\n"
                "字数：期望的总字数\n"
                "#例如：#\n"
                "主题：张家界实景三维大屏展示系统项目建设方案\n"
                "字数：30000\n"
                
                ).send()

@cl.on_message
async def main(message: cl.Message):
    generator = cl.user_session.get("generator")
    print(f"[DEBUG] Received message: {message.content}")
    
    if not generator.title:
        try:
            lines = message.content.split('\n')
            for line in lines:
                if line.startswith('主题：'):
                    generator.title = line.replace('主题：', '').strip()
                elif line.startswith('概述：'):
                    generator.overview = line.replace('概述：', '').strip()
                elif line.startswith('字数：'):
                    generator.total_words = int(line.replace('字数：', '').strip())
            
            # Generate summary
            await cl.Message(content="正在生成摘要...").send()
            
            summary_chain = LLMChain(
                llm=generator.llm,
                prompt=PromptTemplate(
                    template=SUMMARY_TEMPLATE,
                    input_variables=["title"]
                )
            )
            
            generator.summary = await cl.make_async(summary_chain.run)(
                title=generator.title
            )
            print(f"[DEBUG] Generated summary:\n{generator.summary}")
            
            # Generate outline
            await cl.Message(content="正在生成大纲...").send()
            
            outline_chain = LLMChain(
                llm=generator.llm,
                prompt=PromptTemplate(
                    template=OUTLINE_TEMPLATE,
                    input_variables=["title", "summary", "total_words"]
                )
            )
            
            outline_result = await cl.make_async(outline_chain.run)(
                title=generator.title,
                summary=generator.summary,
                total_words=generator.total_words
            )
            
            generator.outline_root = parse_outline(outline_result, generator.title)
            
            await cl.Message(
                content=f"已生成摘要和大纲：\n\n"
                        f"摘要：\n{generator.summary}\n\n"
                        f"大纲：\n{outline_result}\n\n"
                        f"请输入：\n"
                        f"1. '继续生成' - 开始生成正文\n"
                        f"2. '重新生成' - 重新生成大纲").send()
            
        except Exception as e:
            print(f"[ERROR] Error processing input: {str(e)}")
            await cl.Message(content=f"输入格式有误，请重新输入。错误信息：{str(e)}").send()
            
    elif message.content in ["继续生成", "重新生成"]:
        if message.content == "继续生成":
            try:
                # 使用深度优先遍历生成所有内容
                await generator.generate_content_dfs(generator.outline_root)
                
                # 导出文档
                filepath,filename = generator.export_to_word()
                elements = [
                    cl.File(
                        name=filename,  # 使用生成的文件名
                        path=filepath,  # 文件的本地路径
                        display="inline",
                    ),
                ]
                
                await cl.Message(
                    content="报告生成完成！已导出到文件：", elements=elements
                ).send()
                
                # 下载文件到 本地
                
            except Exception as e:
                print(f"[ERROR] Failed to generate content: {str(e)}")
                await cl.Message(content=f"生成内容时发生错误：{str(e)}").send() 