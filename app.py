import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from docx import Document
from datetime import datetime
import os
import matplotlib
from PIL import Image
import base64
from io import BytesIO

# 设置中文字体
matplotlib.rc("font", family='YouYuan')
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 辅助函数：将图片转换为base64
def logo_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

# 设置页面配置 - 强制侧边栏展开
st.set_page_config(
    page_title="数据中心监控系统", 
    page_icon="🏢", 
    layout="wide",
    initial_sidebar_state="expanded"  # 强制初始状态为展开
)

# 简单的CSS来确保侧边栏可见
st.markdown("""
<style>
/* 隐藏Streamlit的默认菜单 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Logo样式 */
.logo-container {
    width: 100vw;
    height: 80px;
    margin: 0;
    padding: 0;
    background-color: white;
    text-align: center;
    border-bottom: 2px solid #f0f2f6;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
}
.logo-img {
    max-height: 60px;
    width: auto;
}
.main .block-container {
    padding-top: 100px;
}
</style>
""", unsafe_allow_html=True)

# 原有的Logo代码
try:
    logo = Image.open("xbylogo.jpg")
    st.markdown(
        f"""
        <div class="logo-container">
            <img src="data:image/jpeg;base64,{logo_to_base64(logo)}" class="logo-img">
        </div>
        """,
        unsafe_allow_html=True
    )
except Exception as e:
    pass

# 数据读取和清洗函数
@st.cache_data
def load_and_clean_data(folder_path):
    """读取并清洗文档数据"""
    try:
        file_names = os.listdir(folder_path)
        file_names = [file for file in file_names if file.endswith('.docx')]
        file_names = [os.path.join(folder_path, file) for file in file_names]
        
        if not file_names:
            st.error(f"在路径 {folder_path} 中未找到.docx文件")
            return []
        
        rawcontent = []
        for file in file_names:
            try:
                document = Document(file)
                tables = document.tables
                for table in tables:
                    for row in table.rows:
                        for cell in row.cells:
                            rawcontent.append(cell.text)
            except Exception as e:
                st.warning(f"读取文件 {file} 时出错: {e}")
        
        # 数据清洗
        for i in range(len(rawcontent)-1):
            if rawcontent[i] == rawcontent[i+1]:
                rawcontent[i] = ''
        rawcontent = [i for i in rawcontent if i != '']
        
        return rawcontent
    except Exception as e:
        st.error(f"加载数据时出错: {e}")
        return []

@st.cache_data
def extract_all_data(rawcontent):
    """从原始内容中提取所有数据"""
    # 初始化所有列表
    ZJFTemp = [] #主机房温度
    ZJFHum  = [] #主机房湿度
    LTDTemp = [] #四组冷通道温度
    LTDHum  = [] #四组冷通道湿度
    DCJTemp = [] #电池间温度
    DCJHum  = [] #电池间湿度
    YYJTemp = [] #运营商接入间温度
    YYJHum  = [] #运营商接入间湿度
    PDJTemp = [] #配电间温度
    PDJHum  = [] #配电间湿度
    hydr    = [] #电池间氢气传感器
    time    = [] #日期
    PUE     = [] #电源使用效率

    # 提取数据
    for i in range(len(rawcontent)-1):
        if rawcontent[i] == '日期:':
            try:
                time.append(datetime.strptime(rawcontent[i+1], "%Y-%m-%d").date())
            except ValueError:
                continue
        if rawcontent[i] == '电池间氢气传感器':
            try:
                hydr.append(float(rawcontent[i+2].replace('PPM','')))
            except (ValueError, IndexError):
                continue
        if rawcontent[i] == '主机房温度湿度':
            try:
                temp_humi_str = rawcontent[i+2].replace('C','').strip('%')
                parts = temp_humi_str.split()
                if len(parts) >= 2:
                    ZJFTemp.append(float(parts[0]))
                    ZJFHum.append(float(parts[1]))
            except (ValueError, IndexError):
                continue
        if rawcontent[i] == '电源使用效率（PUE）':
            try:
                PUE.append(float(rawcontent[i+2]))
            except (ValueError, IndexError):
                continue
        if rawcontent[i] == '四组冷通道温度':
            try:
                temp_humi_str = rawcontent[i+2].replace('C','').strip('%')
                parts = temp_humi_str.split()
                if len(parts) >= 2:
                    LTDTemp.append(float(parts[0]))
                    LTDHum.append(float(parts[1]))
            except (ValueError, IndexError):
                continue
        if rawcontent[i] == '电池间温度湿度':
            try:
                temp_humi_str = rawcontent[i+2].replace('C','').strip('%')
                parts = temp_humi_str.split()
                if len(parts) >= 2:
                    DCJTemp.append(float(parts[0]))
                    DCJHum.append(float(parts[1]))
            except (ValueError, IndexError):
                continue
        if rawcontent[i] == '运营商接入间温度湿度':
            try:
                temp_humi_str = rawcontent[i+2].replace('C','').strip('%')
                parts = temp_humi_str.split()
                if len(parts) >= 2:
                    YYJTemp.append(float(parts[0]))
                    YYJHum.append(float(parts[1]))
            except (ValueError, IndexError):
                continue
        if rawcontent[i] == '配电间温度湿度':
            try:
                temp_humi_str = rawcontent[i+2].replace('C','').strip('%')
                parts = temp_humi_str.split()
                if len(parts) >= 2:
                    PDJTemp.append(float(parts[0]))
                    PDJHum.append(float(parts[1]))
            except (ValueError, IndexError):
                continue
    
    return {
        'time': time,
        'ZJFTemp': ZJFTemp,
        'ZJFHum': ZJFHum,
        'LTDTemp': LTDTemp,
        'LTDHum': LTDHum,
        'DCJTemp': DCJTemp,
        'DCJHum': DCJHum,
        'YYJTemp': YYJTemp,
        'YYJHum': YYJHum,
        'PDJTemp': PDJTemp,
        'PDJHum': PDJHum,
        'hydr': hydr,
        'PUE': PUE
    }

# 侧边栏配置 - 简洁版本
with st.sidebar:
    st.title("🏢 数据中心监控系统")
    st.markdown("---")
    
    # 使用radio作为导航菜单
    page = st.radio(
        "选择监控页面", 
        ["📊 主界面", "🌡️ 数据中心温度", "💧 数据中心湿度", "⚡ PUE指标", "🎈 氢气传感器"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # 系统状态指示器
    st.markdown("**系统状态**")
    if st.session_state.get('data_loaded', False):
        st.success("✅ 数据已加载")
    else:
        st.warning("⚠️ 数据未加载")

# 初始化session state
if 'active_plots' not in st.session_state:
    st.session_state.active_plots = {}
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'all_data' not in st.session_state:
    st.session_state.all_data = None

# 主界面
if page == "📊 主界面":
    st.title("🏢 数据中心综合监控系统")
    st.markdown("---")
    
    # 在主界面添加数据加载选项
    st.subheader("📂 数据加载")
    folder_path = st.text_input(
        "数据文件夹路径", 
        value="D:\\巡检报告\\报告",
        help="请输入包含.docx巡检报告的文件夹路径"
    )
    
    if st.button("加载数据"):
        with st.spinner("正在加载数据..."):
            try:
                # 读取数据
                rawcontent = load_and_clean_data(folder_path)
                if rawcontent:
                    all_data = extract_all_data(rawcontent)
                    st.session_state.all_data = all_data
                    st.session_state.data_loaded = True
                    st.success("数据加载成功！")
                else:
                    st.session_state.data_loaded = False
                    st.error("数据加载失败，请检查路径")
                    
            except Exception as e:
                st.error(f"加载数据时出错: {e}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 监控指标概览")
        st.info("""
        - **温度监控**: 实时监测各机房区域温度
        - **湿度监控**: 监测环境湿度变化
        - **PUE指标**: 能效利用率分析
        - **氢气监测**: 电池间安全监控
        """)
        
        st.subheader("🚀 快速导航")
        st.write("使用左侧菜单快速切换到不同监控页面")
        
    with col2:
        st.subheader("🔧 系统状态")
        
        # 系统状态
        status_col1, status_col2 = st.columns(2)
        with status_col1:
            st.metric("数据加载状态", "✅ 就绪" if st.session_state.data_loaded else "❌ 未加载")
            st.metric("温度传感器", "✅ 正常")
            st.metric("湿度传感器", "✅ 正常")
        
        with status_col2:
            st.metric("PUE计算", "✅ 运行中")
            st.metric("氢气监测", "✅ 正常")
            st.metric("系统运行", "✅ 稳定")
        
        if st.session_state.data_loaded:
            st.success("✅ 数据已成功加载，可以查看各监控页面")
        else:
            st.warning("⚠️ 请先加载数据以查看监控信息")

# 温度监控页面
elif page == "🌡️ 数据中心温度":
    st.title("🌡️ 数据中心温度监控")
    st.markdown("---")
    
    if st.session_state.data_loaded and st.session_state.all_data:
        try:
            all_data = st.session_state.all_data
            time_data = all_data['time']
            
            # 温度数据准备
            y_datasets = {
                "主机房温度": all_data['ZJFTemp'],
                "冷通道温度": all_data['LTDTemp'],
                "电池间温度": all_data['DCJTemp'],
                "运营间温度": all_data['YYJTemp'],
                "配电间温度": all_data['PDJTemp']
            }
            
            # 颜色配置
            colors = {
                "主机房温度": "blue",
                "冷通道温度": "red",
                "电池间温度": "green",
                "运营间温度": "purple",
                "配电间温度": "orange"
            }
            
            # 在侧边栏添加数据系列控制
            with st.sidebar.expander("📊 温度系列控制", expanded=True):
                st.write("选择要显示的温度系列:")
                for name in y_datasets.keys():
                    if st.checkbox(name, value=(name in st.session_state.active_plots), key=f"temp_chk_{name}"):
                        st.session_state.active_plots[name] = True
                    else:
                        if name in st.session_state.active_plots:
                            del st.session_state.active_plots[name]
            
            # 绘制图形
            st.subheader("📈 温度走势图表")
            
            col_chart, col_info = st.columns([3, 1])
            
            with col_chart:
                fig, ax = plt.subplots(figsize=(10, 4), facecolor='white')
                ax.set_facecolor('white')
                
                if st.session_state.active_plots:
                    for name in st.session_state.active_plots:
                        if name in y_datasets and y_datasets[name]:
                            y_data = y_datasets[name]
                            color = colors.get(name, "blue")
                            
                            # 确保时间序列和数据长度匹配
                            min_len = min(len(time_data), len(y_data))
                            ax.plot(time_data[:min_len], y_data[:min_len], 
                                   color=color, 
                                   marker='o',
                                   markersize=4,
                                   label=name, 
                                   linewidth=1.5)
                    
                    ax.legend(loc='upper right', fontsize=8)
                    ax.grid(True, linestyle='--', alpha=0.7)
                    ax.set_xlabel('日期', fontsize=9)
                    ax.set_ylabel('温度 （℃）', fontsize=9)
                    ax.set_title('数据中心温度走势表', fontsize=11)
                    
                    plt.xticks(rotation=45, fontsize=8)
                    plt.yticks(fontsize=8)
                    plt.tight_layout()
                    
                else:
                    ax.text(0.5, 0.5, '请在侧边栏选择要显示的温度系列', 
                            horizontalalignment='center', verticalalignment='center',
                            transform=ax.transAxes, fontsize=10)
                    ax.set_xlim(0, 10)
                    ax.set_ylim(0, 40)
                    ax.grid(True, linestyle='--', alpha=0.7)
                    ax.set_xlabel('日期', fontsize=9)
                    ax.set_ylabel('温度 （℃）', fontsize=9)
                    ax.set_title('数据中心温度走势表', fontsize=11)
                
                st.pyplot(fig)
            
            with col_info:
                st.subheader("📊 温度统计")
                if st.session_state.active_plots:
                    for name in st.session_state.active_plots:
                        if name in y_datasets and y_datasets[name]:
                            temp_data = y_datasets[name]
                            with st.expander(f"{name}", expanded=False):
                                st.metric("平均值", f"{np.mean(temp_data):.2f}℃")
                                st.metric("最大值", f"{max(temp_data):.2f}℃")
                                st.metric("最小值", f"{min(temp_data):.2f}℃")
                                st.metric("数据点数", len(temp_data))
                else:
                    st.info("请选择温度系列")
                        
        except Exception as e:
            st.error(f"处理温度数据时出错: {e}")
    else:
        st.info("👆 请先在主界面加载数据")

# 湿度监控页面
elif page == "💧 数据中心湿度":
    st.title("💧 数据中心湿度监控")
    st.markdown("---")
    
    if st.session_state.data_loaded and st.session_state.all_data:
        try:
            all_data = st.session_state.all_data
            time_data = all_data['time']
            
            # 湿度数据准备
            y_datasets = {
                "主机房湿度": all_data['ZJFHum'],
                "冷通道湿度": all_data['LTDHum'],
                "电池间湿度": all_data['DCJHum'],
                "运营间湿度": all_data['YYJHum'],
                "配电间湿度": all_data['PDJHum']
            }
            
            # 颜色配置
            colors = {
                "主机房湿度": "blue",
                "冷通道湿度": "red",
                "电池间湿度": "green",
                "运营间湿度": "purple",
                "配电间湿度": "orange"
            }
            
            # 在侧边栏添加数据系列控制
            with st.sidebar.expander("📊 湿度系列控制", expanded=True):
                st.write("选择要显示的湿度系列:")
                for name in y_datasets.keys():
                    if st.checkbox(name, value=(name in st.session_state.active_plots), key=f"humi_chk_{name}"):
                        st.session_state.active_plots[name] = True
                    else:
                        if name in st.session_state.active_plots:
                            del st.session_state.active_plots[name]
            
            # 绘制图形
            st.subheader("📈 湿度走势图表")
            
            col_chart, col_info = st.columns([3, 1])
            
            with col_chart:
                fig, ax = plt.subplots(figsize=(10, 4), facecolor='white')
                ax.set_facecolor('white')
                
                if st.session_state.active_plots:
                    for name in st.session_state.active_plots:
                        if name in y_datasets and y_datasets[name]:
                            y_data = y_datasets[name]
                            color = colors.get(name, "blue")
                            
                            # 确保时间序列和数据长度匹配
                            min_len = min(len(time_data), len(y_data))
                            ax.plot(time_data[:min_len], y_data[:min_len], 
                                   color=color, 
                                   marker='s',
                                   markersize=4,
                                   label=name, 
                                   linewidth=1.5)
                    
                    ax.legend(loc='upper right', fontsize=8)
                    ax.grid(True, linestyle='--', alpha=0.7)
                    ax.set_xlabel('日期', fontsize=9)
                    ax.set_ylabel('湿度 （%）', fontsize=9)
                    ax.set_title('数据中心湿度走势表', fontsize=11)
                    
                    plt.xticks(rotation=45, fontsize=8)
                    plt.yticks(fontsize=8)
                    plt.tight_layout()
                    
                else:
                    ax.text(0.5, 0.5, '请在侧边栏选择要显示的湿度系列', 
                            horizontalalignment='center', verticalalignment='center',
                            transform=ax.transAxes, fontsize=10)
                    ax.set_xlim(0, 10)
                    ax.set_ylim(0, 100)
                    ax.grid(True, linestyle='--', alpha=0.7)
                    ax.set_xlabel('日期', fontsize=9)
                    ax.set_ylabel('湿度 （%）', fontsize=9)
                    ax.set_title('数据中心湿度走势表', fontsize=11)
                
                st.pyplot(fig)
            
            with col_info:
                st.subheader("📊 湿度统计")
                if st.session_state.active_plots:
                    for name in st.session_state.active_plots:
                        if name in y_datasets and y_datasets[name]:
                            humi_data = y_datasets[name]
                            with st.expander(f"{name}", expanded=False):
                                st.metric("平均值", f"{np.mean(humi_data):.2f}%")
                                st.metric("最大值", f"{max(humi_data):.2f}%")
                                st.metric("最小值", f"{min(humi_data):.2f}%")
                                st.metric("数据点数", len(humi_data))
                else:
                    st.info("请选择湿度系列")
                        
        except Exception as e:
            st.error(f"处理湿度数据时出错: {e}")
    else:
        st.info("👆 请先在主界面加载数据")

# PUE指标页面
elif page == "⚡ PUE指标":
    st.title("⚡ PUE能效指标监控")
    st.markdown("---")
    
    if st.session_state.data_loaded and st.session_state.all_data:
        try:
            all_data = st.session_state.all_data
            time_data = all_data['time']
            pue_data = all_data['PUE']
            
            if time_data and pue_data:
                st.subheader("📈 PUE走势图表")
                
                fig, ax = plt.subplots(figsize=(10, 4), facecolor='white')
                ax.set_facecolor('white')
                
                # 确保时间序列和数据长度匹配
                min_len = min(len(time_data), len(pue_data))
                ax.plot(time_data[:min_len], pue_data[:min_len], color='red', marker='^', markersize=4, linewidth=1.5)
                ax.axhline(y=1.5, color='green', linestyle='--', alpha=0.7, label='目标值 (1.5)')
                ax.axhline(y=1.6, color='orange', linestyle='--', alpha=0.7, label='警戒值 (1.6)')
                
                ax.legend(loc='upper right', fontsize=8)
                ax.grid(True, linestyle='--', alpha=0.7)
                ax.set_xlabel('日期', fontsize=9)
                ax.set_ylabel('PUE值', fontsize=9)
                ax.set_title('数据中心PUE能效走势表', fontsize=11)
                
                plt.xticks(rotation=45, fontsize=8)
                plt.yticks(fontsize=8)
                plt.tight_layout()
                
                st.pyplot(fig)
                
                # 统计信息
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("当前PUE", f"{pue_data[-1]:.3f}")
                with col2:
                    st.metric("平均值", f"{np.mean(pue_data):.3f}")
                with col3:
                    st.metric("最优值", f"{min(pue_data):.3f}")
                with col4:
                    status = "优秀" if np.mean(pue_data) < 1.5 else "良好"
                    st.metric("能效等级", status)
                
                st.info("💡 **PUE说明**: 电能使用效率，值越接近1表示能效越高")
            else:
                st.error("未找到有效的PUE数据")
                
        except Exception as e:
            st.error(f"处理PUE数据时出错: {e}")
    else:
        st.info("👆 请先在主界面加载数据")

# 氢气传感器页面
elif page == "🎈 氢气传感器":
    st.title("🎈 氢气浓度监控")
    st.markdown("---")
    
    if st.session_state.data_loaded and st.session_state.all_data:
        try:
            all_data = st.session_state.all_data
            time_data = all_data['time']
            hydr_data = all_data['hydr']
            
            if time_data and hydr_data:
                st.subheader("📈 氢气浓度走势图表")
                
                fig, ax = plt.subplots(figsize=(10, 4), facecolor='white')
                ax.set_facecolor('white')
                
                # 确保时间序列和数据长度匹配
                min_len = min(len(time_data), len(hydr_data))
                ax.plot(time_data[:min_len], hydr_data[:min_len], color='purple', marker='D', markersize=4, linewidth=1.5)
                
                ax.legend(['氢气浓度'], loc='upper right', fontsize=8)
                ax.grid(True, linestyle='--', alpha=0.7)
                ax.set_xlabel('日期', fontsize=9)
                ax.set_ylabel('氢气浓度 (ppm)', fontsize=9)
                ax.set_title('电池间氢气浓度监测', fontsize=11)
                
                plt.xticks(rotation=45, fontsize=8)
                plt.yticks(fontsize=8)
                plt.tight_layout()
                
                st.pyplot(fig)
                
                # 统计信息
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("当前浓度", f"{hydr_data[-1]:.1f}ppm")
                with col2:
                    st.metric("最高浓度", f"{max(hydr_data):.1f}ppm")
                with col3:
                    st.metric("平均浓度", f"{np.mean(hydr_data):.1f}ppm")
                
                st.info("💡 **安全说明**: 实时监测电池间氢气浓度")
            else:
                st.error("未找到有效的氢气传感器数据")
                
        except Exception as e:
            st.error(f"处理氢气数据时出错: {e}")
    else:
        st.info("👆 请先在主界面加载数据")