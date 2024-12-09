import unittest
from report_generator import parse_outline, OutlineNode

class TestReportGenerator(unittest.TestCase):
    
    def test_parse_outline(self):
        outline_text = """
# 张家界实景三维大屏展示系统项目建设方案报告大纲                                                                                  
                                                                                                                                  
1. 引言 (3000字)                                                                                                                  
    1.1 项目背景 (1000字)                                                                                                         
    1.2 研究目的与意义 (1000字)                                                                                                   
    1.3 报告结构概述 (1000字)                                                                                                     
                                                                                                                                  
2. 项目概述 (4000字)                                                                                                              
    2.1 张家界旅游资源概述 (1500字)                                                                                               
    2.2 三维大屏展示系统的定义与功能 (1500字)                                                                                     
    2.3 项目目标与预期成果 (1000字)                                                                                               
                                                                                                                                  
3. 系统架构 (5000字)                                                                                                              
    3.1 系统整体架构设计 (2000字)                                                                                                 
    3.2 硬件配置与选型 (1500字)                                                                                                   
    3.3 软件架构设计 (1500字)                                                                                                     
                                                                                                                                  
4. 技术选型 (5000字)                                                                                                              
    4.1 三维可视化技术分析 (2000字)                                                                                               
    4.2 数据处理与存储技术 (1500字)                                                                                               
    4.3 交互技术与用户体验设计 (1500字)                                                                                           
                                                                                                                                  
5. 内容制作 (5000字)                                                                                                              
    5.1 内容策划与需求分析 (2000字)                                                                                               
    5.2 三维模型与动画制作 (2000字)                                                                                               
    5.3 多媒体内容整合 (1000字)                                                                                                   
                                                                                                                                  
6. 维护与管理 (3000字)                                                                                                            
    6.1 系统维护的必要性 (1000字)                                                                                                 
    6.2 维护管理流程 (1000字)                                                                                                     
    6.3 数据更新与内容管理 (1000字)                                                                                               
                                                                                                                                  
7. 市场分析与推广策略 (4000字)                                                                                                    
    7.1 目标用户群体分析 (1500字)                                                                                                 
    7.2 竞争分析与市场机会 (1500字)                                                                                               
    7.3 推广策略与渠道 (1000字)                                                                                                   
                                                                                                                                  
8. 项目实施步骤 (3000字)
    8.1 项目规划阶段 (1000字)
    8.2 实施与监控阶段 (1000字)
    8.3 项目评估与反馈 (1000字)

9. 经济效益分析 (3000字)
    9.1 投资预算与成本控制 (1000字)
    9.2 经济效益预测 (1000字)
    9.3 社会效益与文化传播 (1000字)

10. 结论与展望 (2000字)
    10.1 项目总结 (1000字)
    10.2 未来发展方向 (1000字)

---

**总字数：30000字**

"""

        outline_text = """
# 晋城市智慧水务-数字孪生底座建设方案报告大纲                                                                                     
                                                                                                                                  
## 1. 引言 (3000字)                                                                                                               
   1.1 背景与意义 (1500字)                                                                                                        
   1.2 研究目的与方法 (1500字)                                                                                                    
                                                                                                                                  
## 2. 数字孪生技术概述 (5000字)                                                                                                   
   2.1 数字孪生的定义与发展 (2000字)                                                                                              
   2.2 数字孪生的关键技术 (2000字)                                                                                                
   2.3 数字孪生在水务管理中的应用 (1000字)                                                                                        
                                                                                                                                  
 ## 3. 晋城市水务现状分析 (4000字)                                                                                                 
   3.1 水务管理现状 (2000字)                                                                                                      
   3.2 存在的问题与挑战 (2000字)                                                                                                  
                                                                                                                                  
 ## 4. 数字孪生底座建设方案 (8000字)                                                                                               
   4.1 建设目标与愿景 (2000字)                                                                                                    
   4.2 技术架构设计 (3000字)                                                                                                      
       4.2.1 数据采集层 (1000字)                                                                                                  
       4.2.2 数据传输层 (1000字)                                                                                                  
       4.2.3 数据处理层 (1000字)                                                                                                  
   4.3 实施步骤 (3000字)                                                                                                          
       4.3.1 需求分析 (1000字)                                                                                                    
       4.3.2 系统开发与测试 (1000字)                                                                                              
       4.3.3 部署与运营 (1000字)                                                                                                  
                                                                                                                                  
## 5. 实施案例分析 (4000字)                                                                                                       
   5.1 国内外成功案例 (2000字)                                                                                                    
   5.2 案例对比与启示 (2000字)                                                                                                    
                                                                                                                                  
## 6. 数字孪生底座的效益分析 (4000字)                                                                                             
   6.1 经济效益 (2000字)                                                                                                          
   6.2 社会效益 (2000字)                                                                                                          
                                                                                                                                  
## 7. 持续改进与未来展望 (3000字)                                                                                                 
   7.1 持续改进机制 (1500字)                                                                                                      
   7.2 未来发展趋势 (1500字)                                                                                                      



"""
        root = parse_outline(outline_text, "张家界实景三维大屏展示系统项目建设方案报告大纲")
        
        # Check root node
        self.assertEqual(root.title, "张家界实景三维大屏展示系统项目建设方案报告大纲")
        self.assertEqual(len(root.children), 10)  # Should have 10 main sections
        
        # Check first section
        first_section = root.children[0]
        self.assertEqual(first_section.title, "引言")
        self.assertEqual(first_section.words, 3000)
        self.assertEqual(len(first_section.children), 3)  # Should have 3 subsections
        
        # Check first subsection
        first_subsection = first_section.children[0]
        self.assertEqual(first_subsection.title, "项目背景")
        self.assertEqual(first_subsection.words, 1000)

        # Check total word count
        total_words = sum(section.words for section in root.children)
        self.assertEqual(total_words, 37000)

if __name__ == '__main__':
    unittest.main() 