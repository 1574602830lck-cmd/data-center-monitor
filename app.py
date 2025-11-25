import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import base64
from io import BytesIO
import pandas as pd
import requests
import random
import os
import matplotlib.font_manager as fm

# 强制使用当前目录的字体文件
def setup_chinese_font():
    """强制使用当前目录的字体文件，如果找不到则报错"""
    try:
        # 1. 强制查找当前目录的字体文件
        current_dir_fonts = [
            'SimHei.ttf',  # 主要字体
            'simhei.ttf',  # 小写版本
        ]
        
        font_path = None
        
        # 强制检查当前目录
        for font_file in current_dir_fonts:
            if os.path.exists(font_file):
                font_path = os.path.abspath(font_file)
                break
        
        # 2. 如果找不到字体文件，抛出错误
        if not font_path:
            raise FileNotFoundError("未在当前目录找到 SimHei.ttf 字体文件")
        
        # 3. 强制设置字体
        # 清除字体缓存
        if hasattr(fm, '_rebuild'):
            fm._rebuild()
        
        # 设置字体属性
        font_prop = fm.FontProperties(fname=font_path)
        
        # 强制设置全局字体
        plt.rcParams['font.family'] = [font_prop.get_name()]
        plt.rcParams['font.sans-serif'] = [font_prop.get_name()]
        plt.rcParams['axes.unicode_minus'] = False
        
        # 验证字体是否生效
        test_fig, test_ax = plt.subplots(figsize=(2, 1))
        test_ax.text(0.5, 0.5, '中文测试', fontproperties=font_prop, 
                    ha='center', va='center', fontsize=12)
        test_ax.set_xlim(0, 1)
        test_ax.set_ylim(0, 1)
        test_ax.axis('off')
        plt.close(test_fig)
        
        return font_path
        
    except Exception as e:
        st.error(f"字体设置失败: {str(e)}")
        st.error("请确保 SimHei.ttf 文件在当前目录中")
        # 如果失败，停止程序运行
        st.stop()
        return None

# 初始化字体
font_path = setup_chinese_font()

def get_font_properties():
    """获取字体属性"""
    try:
        return fm.FontProperties(fname=font_path)
    except:
        return None

def logo_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

# 设置页面
st.set_page_config(
    page_title="数据中心监控系统", 
    page_icon="🏢", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS样式优化 - 移动端适配
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* 移动端适配 */
@media (max-width: 768px) {
    .logo-container {
        height: 80px !important;
    }
    
    .stats-card {
        padding: 15px !important;
        margin-bottom: 10px !important;
    }
    
    .stats-card .value {
        font-size: 1.5em !important;
    }
    
    .metric-card {
        padding: 15px !important;
        margin-bottom: 10px !important;
    }
    
    /* 移动端列布局调整 */
    .mobile-columns {
        flex-direction: column;
    }
    
    /* 移动端按钮调整 */
    .stButton button {
        font-size: 14px !important;
        padding: 8px 12px !important;
    }
}

.logo-container {
    height: 120px;
    background: white;
    text-align: center;
    border-bottom: 2px solid #f0f2f6;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 0px;
    border-radius: 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    overflow: hidden;
}
.logo-img {
    height: 100%;
    width: auto;
    object-fit: contain;
    max-width: 100%;
}

/* 新版数据统计卡片样式 */
.stats-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 15px;
    padding: 20px;
    color: white;
    margin-bottom: 15px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    border: none;
}

.stats-card h3 {
    color: white;
    font-size: 0.9em;
    margin-bottom: 10px;
    opacity: 0.9;
}

.stats-card .value {
    font-size: 2em;
    font-weight: bold;
    margin-bottom: 5px;
}

.stats-card .subtitle {
    font-size: 0.8em;
    opacity: 0.8;
}

/* 数据质量指示器 */
.data-quality {
    display: flex;
    align-items: center;
    margin-top: 10px;
    font-size: 0.8em;
}

.quality-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 6px;
}

.quality-excellent { background-color: #00d26a; }
.quality-good { background-color: #00b8d9; }
.quality-fair { background-color: #ffab00; }
.quality-poor { background-color: #ff5630; }

/* 进度条样式 */
.progress-container {
    background: rgba(255,255,255,0.2);
    border-radius: 10px;
    height: 6px;
    margin-top: 8px;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    border-radius: 10px;
    background: linear-gradient(90deg, #00d26a, #00b8d9);
    transition: width 0.3s ease;
}

/* 指标卡片样式 */
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    border-left: 4px solid #667eea;
    margin-bottom: 15px;
    transition: transform 0.2s ease;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
}

/* 移动端图表容器 */
.chart-container {
    width: 100%;
    overflow-x: auto;
}

/* 移动端区域选择按钮 */
.area-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 15px;
}

.area-button {
    flex: 1;
    min-width: 80px;
}

/* 移动端统计卡片 */
.stat-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 15px;
}

.stat-item {
    flex: 1;
    min-width: 120px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
    padding: 15px;
    color: white;
    text-align: center;
}

.stat-value {
    font-size: 1.2em;
    font-weight: bold;
    margin: 5px 0;
}

.stat-label {
    font-size: 0.8em;
    opacity: 0.9;
}
</style>
""", unsafe_allow_html=True)

# Logo处理 - 放在最顶部
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
except:
    st.markdown(
        """
        <div class="logo-container">
            <h2 style="color: #333; margin: 0;">🏢 数据中心监控系统</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

@st.cache_data(ttl=3600)
def load_data_from_github():
    """从GitHub自动读取数据"""
    try:
        url = "https://raw.githubusercontent.com/1574602830lck-cmd/data-center-monitor/1ae0c6874e16ad216a229cc1451e8dfed81e282d/data_centre_df.csv"
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        df = pd.read_csv(BytesIO(response.content))
        
        all_data = {
            'time': [], 'ZJFTemp': [], 'ZJFHum': [], 'LTDTemp': [], 'LTDHum': [],
            'DCJTemp': [], 'DCJHum': [], 'YYJTemp': [], 'YYJHum': [], 'PDJTemp': [],
            'PDJHum': [], 'hydr': [], 'PUE': []
        }
        
        # 日期列处理
        date_columns = [col for col in df.columns if col.lower() in ['record_date', 'date', '时间', '日期']]
        if date_columns:
            all_data['time'] = pd.to_datetime(df[date_columns[0]]).dt.date.tolist()
        else:
            all_data['time'] = list(range(1, len(df) + 1))
        
        # 列映射
        column_mapping = {
            'computer_room_temp': 'ZJFTemp', 'computer_room_humidity': 'ZJFHum',
            'cold_aisle_temp': 'LTDTemp', 'cold_aisle_humidity': 'LTDHum',
            'battery_room_temp': 'DCJTemp', 'battery_room_humidity': 'DCJHum',
            'carrier_room_temp': 'YYJTemp', 'carrier_room_humidity': 'YYJHum',
            'power_room_temp': 'PDJTemp', 'power_room_humidity': 'PDJHum',
            'hydrogen_sensor': 'hydr', 'pue': 'PUE'
        }
        
        for csv_col, internal_key in column_mapping.items():
            if csv_col in df.columns:
                all_data[internal_key] = pd.to_numeric(df[csv_col], errors='coerce').fillna(0).tolist()
            else:
                all_data[internal_key] = [0] * len(df)
        
        return all_data, True
        
    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return None, False

# 侧边栏
with st.sidebar:
    st.title("🏢 数据中心监控系统")
    st.markdown("---")
    page = st.radio(
        "选择监控页面", 
        ["📊 主界面", "🌡️ 数据中心温度", "💧 数据中心湿度", "⚡ PUE指标", "🎈 氢气传感器"],
        label_visibility="collapsed"
    )

# 初始化状态
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'all_data' not in st.session_state:
    st.session_state.all_data = None

# 初始化温度页面区域选择状态 - 默认只选择两个随机区域
if 'temp_areas' not in st.session_state:
    areas = ['主机房', '冷通道', '电池间', '运营间', '配电间']
    # 随机选择两个区域
    selected_areas = random.sample(areas, 2)
    st.session_state.temp_areas = {area: (area in selected_areas) for area in areas}

# 初始化湿度页面区域选择状态 - 默认只选择两个随机区域
if 'hum_areas' not in st.session_state:
    areas = ['主机房', '冷通道', '电池间', '运营间', '配电间']
    # 随机选择两个区域
    selected_areas = random.sample(areas, 2)
    st.session_state.hum_areas = {area: (area in selected_areas) for area in areas}

# 自动加载数据
if not st.session_state.data_loaded:
    with st.spinner("🔄 正在从GitHub加载数据..."):
        all_data, success = load_data_from_github()
        if success and all_data:
            st.session_state.all_data = all_data
            st.session_state.data_loaded = True

# 图表绘制函数 - 移动端适配
def plot_recent_data(time_data, data_dict, title, ylabel, colors=None, recent_points=10):
    if colors is None:
        colors = ['red', 'blue', 'green', 'orange', 'purple']
    
    # 获取字体属性
    font_prop = get_font_properties()
    
    # 移动端适配的图表大小
    fig_width = 8 if st.session_state.get('is_mobile', False) else 10
    fig_height = 3 if st.session_state.get('is_mobile', False) else 4
    
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    has_data = False
    
    for i, (label, data) in enumerate(data_dict.items()):
        if data and any(x != 0 for x in data):
            # 只取最近的数据点
            valid_data = [x for x in data if x != 0]
            valid_times = [time_data[i] for i, x in enumerate(data) if x != 0]
            
            if len(valid_data) > recent_points:
                valid_data = valid_data[-recent_points:]
                valid_times = valid_times[-recent_points:]
            
            if valid_data:
                ax.plot(valid_times, valid_data, label=label, color=colors[i % len(colors)], 
                       linewidth=2, marker='o', markersize=3)
                has_data = True
    
    if has_data:
        # 移动端适配的字体大小
        title_size = 10 if st.session_state.get('is_mobile', False) else 12
        label_size = 8 if st.session_state.get('is_mobile', False) else 10
        legend_size = 7 if st.session_state.get('is_mobile', False) else 8
        tick_size = 7 if st.session_state.get('is_mobile', False) else 8
        
        if font_prop:
            ax.set_title(title, fontproperties=font_prop, fontsize=title_size, fontweight='bold')
            ax.set_ylabel(ylabel, fontproperties=font_prop, fontsize=label_size)
            ax.set_xlabel('时间', fontproperties=font_prop, fontsize=label_size)
            ax.legend(prop=font_prop, fontsize=legend_size)
            plt.xticks(rotation=45, fontproperties=font_prop, fontsize=tick_size)
        else:
            ax.set_title(title, fontsize=title_size, fontweight='bold')
            ax.set_ylabel(ylabel, fontsize=label_size)
            ax.set_xlabel('Time', fontsize=label_size)
            ax.legend(fontsize=legend_size)
            plt.xticks(rotation=45, fontsize=tick_size)
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig, True
    return None, False

# 检测移动端
def is_mobile():
    """检测是否为移动端"""
    try:
        # 使用 st.query_params 替代 st.experimental_get_query_params
        user_agent = st.query_params.get('user_agent', '')
        mobile_keywords = ['mobile', 'android', 'iphone', 'ipad']
        return any(keyword in user_agent.lower() for keyword in mobile_keywords)
    except:
        return False

# 设置移动端状态
st.session_state.is_mobile = is_mobile()

# 页面路由
if page == "📊 主界面":
    st.title("数据中心综合监控系统")
    
    if st.session_state.data_loaded and st.session_state.all_data:
        all_data = st.session_state.all_data
        
        # 关键指标 - 移动端适配
        st.subheader("📈 关键指标概览")
        if st.session_state.is_mobile:
            # 移动端使用2x2布局
            col1, col2 = st.columns(2)
            col3, col4 = st.columns(2)
        else:
            col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            temp_data = []
            for key in ['ZJFTemp', 'LTDTemp', 'DCJTemp', 'YYJTemp', 'PDJTemp']:
                if all_data[key] and any(x != 0 for x in all_data[key]):
                    temp_data.extend([x for x in all_data[key] if x != 0])
            st.metric("平均温度", f"{np.mean(temp_data):.1f}℃" if temp_data else "无数据")
        
        with col2:
            hum_data = []
            for key in ['ZJFHum', 'LTDHum', 'DCJHum', 'YYJHum', 'PDJHum']:
                if all_data[key] and any(x != 0 for x in all_data[key]):
                    hum_data.extend([x for x in all_data[key] if x != 0])
            st.metric("平均湿度", f"{np.mean(hum_data):.1f}%" if hum_data else "无数据")
        
        with col3:
            if all_data['PUE'] and any(x != 0 for x in all_data['PUE']):
                latest_pue = [x for x in all_data['PUE'] if x != 0][-1]
                status = "优秀" if latest_pue < 1.5 else "良好" if latest_pue < 1.6 else "需关注"
                st.metric("最新PUE", f"{latest_pue:.1f}", delta=status)
            else:
                st.metric("最新PUE", "无数据")
        
        with col4:
            if all_data['hydr'] and any(x != 0 for x in all_data['hydr']):
                latest_hydr = [x for x in all_data['hydr'] if x != 0][-1]
                status = "安全" if latest_hydr < 50 else "注意"
                st.metric("氢气浓度", f"{latest_hydr:.1f}ppm", delta=status)
            else:
                st.metric("氢气浓度", "无数据")
        
        # 重新设计的数据统计
        st.subheader("📊 数据质量分析")
        
        if st.session_state.is_mobile:
            # 移动端使用2x2布局
            col1, col2 = st.columns(2)
            col3, col4 = st.columns(2)
        else:
            col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # 数据完整性
            total_datasets = len(all_data) - 1  # 减去time字段
            valid_datasets = sum(1 for key in all_data if key != 'time' and any(x != 0 for x in all_data[key]))
            completeness_rate = (valid_datasets / total_datasets) * 100
            
            st.markdown(f"""
            <div class="stats-card">
                <h3>📋 数据完整性</h3>
                <div class="value">{completeness_rate:.1f}%</div>
                <div class="subtitle">{valid_datasets}/{total_datasets} 个数据集</div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {completeness_rate}%"></div>
                </div>
                <div class="data-quality">
                    <div class="quality-dot {'quality-excellent' if completeness_rate > 90 else 'quality-good' if completeness_rate > 70 else 'quality-fair' if completeness_rate > 50 else 'quality-poor'}"></div>
                    {'优秀' if completeness_rate > 90 else '良好' if completeness_rate > 70 else '一般' if completeness_rate > 50 else '需改进'}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # 数据总量
            total_points = sum(len(all_data[key]) for key in all_data if key != 'time')
            valid_points = sum(len([x for x in all_data[key] if x != 0]) for key in all_data if key != 'time')
            valid_rate = (valid_points / total_points) * 100 if total_points > 0 else 0
            
            st.markdown(f"""
            <div class="stats-card">
                <h3>📊 有效数据量</h3>
                <div class="value">{valid_points:,}</div>
                <div class="subtitle">总数据点: {total_points:,}</div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {valid_rate}%"></div>
                </div>
                <div class="data-quality">
                    <div class="quality-dot {'quality-excellent' if valid_rate > 90 else 'quality-good' if valid_rate > 70 else 'quality-fair' if valid_rate > 50 else 'quality-poor'}"></div>
                    有效率: {valid_rate:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # 时间覆盖
            time_points = len(all_data['time'])
            unique_dates = len(set(all_data['time']))
            
            st.markdown(f"""
            <div class="stats-card">
                <h3>⏰ 时间覆盖</h3>
                <div class="value">{time_points}</div>
                <div class="subtitle">数据采集点</div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: 100%"></div>
                </div>
                <div class="data-quality">
                    <div class="quality-dot quality-excellent"></div>
                    {unique_dates} 个不同日期
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            # 数据新鲜度
            if all_data['time'] and len(all_data['time']) > 0:
                latest_date = all_data['time'][-1]
                if isinstance(latest_date, str):
                    days_ago = "今日"
                else:
                    days_ago = "最新"
            else:
                latest_date = "无数据"
                days_ago = "---"
            
            st.markdown(f"""
            <div class="stats-card">
                <h3>🔄 数据更新</h3>
                <div class="value">{days_ago}</div>
                <div class="subtitle">最后更新</div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: 100%"></div>
                </div>
                <div class="data-quality">
                    <div class="quality-dot quality-excellent"></div>
                    {latest_date}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 图表预览 - 移动端适配
        st.subheader("📈 数据趋势预览")
        if st.session_state.is_mobile:
            # 移动端单列显示
            temp_dict = {'主机房': all_data['ZJFTemp'], '冷通道': all_data['LTDTemp']}
            fig, has_data = plot_recent_data(all_data['time'], temp_dict, '温度趋势 (最近数据)', '温度 (℃)', recent_points=6)
            if has_data:
                st.pyplot(fig)
            else:
                st.info("暂无温度数据")
            
            if all_data['PUE'] and any(x != 0 for x in all_data['PUE']):
                pue_dict = {'PUE': all_data['PUE']}
                fig, has_data = plot_recent_data(all_data['time'], pue_dict, 'PUE趋势 (最近数据)', 'PUE值', colors=['blue'], recent_points=6)
                if has_data:
                    ax = fig.axes[0]
                    font_prop = get_font_properties()
                    if font_prop:
                        ax.axhline(y=1.5, color='green', linestyle='--', alpha=0.5, label='目标值 1.5')
                        ax.legend(prop=font_prop)
                    else:
                        ax.axhline(y=1.5, color='green', linestyle='--', alpha=0.5, label='Target 1.5')
                        ax.legend()
                    st.pyplot(fig)
                else:
                    st.info("暂无PUE数据")
            else:
                st.info("暂无PUE数据")
        else:
            # 桌面端双列显示
            col1, col2 = st.columns(2)
            
            with col1:
                temp_dict = {'主机房': all_data['ZJFTemp'], '冷通道': all_data['LTDTemp']}
                fig, has_data = plot_recent_data(all_data['time'], temp_dict, '温度趋势 (最近数据)', '温度 (℃)', recent_points=8)
                if has_data:
                    st.pyplot(fig)
                else:
                    st.info("暂无温度数据")
            
            with col2:
                if all_data['PUE'] and any(x != 0 for x in all_data['PUE']):
                    pue_dict = {'PUE': all_data['PUE']}
                    fig, has_data = plot_recent_data(all_data['time'], pue_dict, 'PUE趋势 (最近数据)', 'PUE值', colors=['blue'], recent_points=8)
                    if has_data:
                        ax = fig.axes[0]
                        font_prop = get_font_properties()
                        if font_prop:
                            ax.axhline(y=1.5, color='green', linestyle='--', alpha=0.5, label='目标值 1.5')
                            ax.legend(prop=font_prop)
                        else:
                            ax.axhline(y=1.5, color='green', linestyle='--', alpha=0.5, label='Target 1.5')
                            ax.legend()
                        st.pyplot(fig)
                    else:
                        st.info("暂无PUE数据")
                else:
                    st.info("暂无PUE数据")
    
    else:
        st.warning("⏳ 正在加载数据，请稍候...")

elif page == "🌡️ 数据中心温度":
    st.title("🌡️ 数据中心温度监控")
    
    if st.session_state.data_loaded and st.session_state.all_data:
        all_data = st.session_state.all_data
        
        # 区域选择 - 移动端适配
        st.subheader("📍 选择监控区域")
        areas = ['主机房', '冷通道', '电池间', '运营间', '配电间']
        
        if st.session_state.is_mobile:
            # 移动端使用2列布局
            cols = st.columns(2)
            for i, area in enumerate(areas):
                with cols[i % 2]:
                    if st.button(area, key=f"btn_{area}", use_container_width=True,
                                type="primary" if st.session_state.temp_areas[area] else "secondary"):
                        st.session_state.temp_areas[area] = not st.session_state.temp_areas[area]
                        st.rerun()
        else:
            cols = st.columns(5)
            for i, area in enumerate(areas):
                with cols[i]:
                    if st.button(area, key=f"btn_{area}", use_container_width=True,
                                type="primary" if st.session_state.temp_areas[area] else "secondary"):
                        st.session_state.temp_areas[area] = not st.session_state.temp_areas[area]
                        st.rerun()
        
        selected = [area for area, selected in st.session_state.temp_areas.items() if selected]
        if selected:
            st.info(f"已选择: {', '.join(selected)}")
        else:
            st.warning("请至少选择一个监控区域")
        
        # 温度图表
        temp_dict = {}
        area_mapping = {
            '主机房': 'ZJFTemp',
            '冷通道': 'LTDTemp', 
            '电池间': 'DCJTemp',
            '运营间': 'YYJTemp',
            '配电间': 'PDJTemp'
        }
        
        for area in areas:
            if st.session_state.temp_areas[area]:
                data_key = area_mapping[area]
                temp_dict[area] = all_data[data_key]
        
        fig, has_data = plot_recent_data(all_data['time'], temp_dict, '数据中心温度监控 (最近数据)', '温度 (℃)', 
                                       recent_points=8 if st.session_state.is_mobile else 12)
        if has_data:
            st.pyplot(fig)
        else:
            st.warning("所选区域暂无温度数据")
        
        # 温度统计 - 移动端适配
        st.subheader("📊 温度统计")
        for area in areas:
            if st.session_state.temp_areas[area]:
                data_key = area_mapping[area]
                data = all_data[data_key]
                valid_data = [x for x in data if x != 0]
                
                if valid_data:
                    latest_temp = valid_data[-1] if valid_data else 0
                    avg_temp = np.mean(valid_data)
                    max_temp = np.max(valid_data)
                    min_temp = np.min(valid_data)
                    
                    st.write(f"**{area}**")
                    if st.session_state.is_mobile:
                        # 移动端使用2x2布局
                        col1, col2 = st.columns(2)
                        col3, col4 = st.columns(2)
                    else:
                        col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("当前温度", f"{latest_temp:.1f}℃")
                    with col2:
                        st.metric("平均温度", f"{avg_temp:.1f}℃")
                    with col3:
                        st.metric("最高温度", f"{max_temp:.1f}℃")
                    with col4:
                        st.metric("最低温度", f"{min_temp:.1f}℃")
                    
                    st.markdown("---")
    
    else:
        st.info("⏳ 数据加载中，请稍候...")

elif page == "💧 数据中心湿度":
    st.title("💧 数据中心湿度监控")
    
    if st.session_state.data_loaded and st.session_state.all_data:
        all_data = st.session_state.all_data
        
        # 区域选择 - 移动端适配
        st.subheader("📍 选择监控区域")
        areas = ['主机房', '冷通道', '电池间', '运营间', '配电间']
        
        if st.session_state.is_mobile:
            # 移动端使用2列布局
            cols = st.columns(2)
            for i, area in enumerate(areas):
                with cols[i % 2]:
                    if st.button(area, key=f"hum_btn_{area}", use_container_width=True,
                                type="primary" if st.session_state.hum_areas[area] else "secondary"):
                        st.session_state.hum_areas[area] = not st.session_state.hum_areas[area]
                        st.rerun()
        else:
            cols = st.columns(5)
            for i, area in enumerate(areas):
                with cols[i]:
                    if st.button(area, key=f"hum_btn_{area}", use_container_width=True,
                                type="primary" if st.session_state.hum_areas[area] else "secondary"):
                        st.session_state.hum_areas[area] = not st.session_state.hum_areas[area]
                        st.rerun()
        
        selected = [area for area, selected in st.session_state.hum_areas.items() if selected]
        if selected:
            st.info(f"已选择: {', '.join(selected)}")
        else:
            st.warning("请至少选择一个监控区域")
        
        # 湿度图表
        hum_dict = {}
        area_mapping = {
            '主机房': 'ZJFHum',
            '冷通道': 'LTDHum', 
            '电池间': 'DCJHum',
            '运营间': 'YYJHum',
            '配电间': 'PDJHum'
        }
        
        for area in areas:
            if st.session_state.hum_areas[area]:
                data_key = area_mapping[area]
                hum_dict[area] = all_data[data_key]
        
        fig, has_data = plot_recent_data(all_data['time'], hum_dict, '数据中心湿度监控 (最近数据)', '湿度 (%)', 
                                       recent_points=8 if st.session_state.is_mobile else 12)
        if has_data:
            st.pyplot(fig)
        else:
            st.warning("所选区域暂无湿度数据")
        
        # 湿度统计 - 移动端适配
        st.subheader("📊 湿度统计")
        for area in areas:
            if st.session_state.hum_areas[area]:
                data_key = area_mapping[area]
                data = all_data[data_key]
                valid_data = [x for x in data if x != 0]
                
                if valid_data:
                    latest_hum = valid_data[-1] if valid_data else 0
                    avg_hum = np.mean(valid_data)
                    max_hum = np.max(valid_data)
                    min_hum = np.min(valid_data)
                    
                    st.write(f"**{area}**")
                    if st.session_state.is_mobile:
                        # 移动端使用2x2布局
                        col1, col2 = st.columns(2)
                        col3, col4 = st.columns(2)
                    else:
                        col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("当前湿度", f"{latest_hum:.1f}%")
                    with col2:
                        st.metric("平均湿度", f"{avg_hum:.1f}%")
                    with col3:
                        st.metric("最高湿度", f"{max_hum:.1f}%")
                    with col4:
                        st.metric("最低湿度", f"{min_hum:.1f}%")
                    
                    st.markdown("---")
    
    else:
        st.info("⏳ 数据加载中，请稍候...")

# 其他页面保持不变...
elif page == "⚡ PUE指标":
    st.title("⚡ PUE能效指标监控")
    
    if st.session_state.data_loaded and st.session_state.all_data:
        all_data = st.session_state.all_data
        
        if all_data['PUE'] and any(x != 0 for x in all_data['PUE']):
            # PUE图表
            fig, has_data = plot_recent_data(all_data['time'], {'PUE': all_data['PUE']}, 'PUE能效指标 (最近数据)', 'PUE值', colors=['blue'], 
                                           recent_points=8 if st.session_state.is_mobile else 12)
            if has_data:
                ax = fig.axes[0]
                font_prop = get_font_properties()
                if font_prop:
                    ax.axhline(y=1.5, color='green', linestyle='--', alpha=0.7, label='优秀目标 (1.5)')
                    ax.axhline(y=1.6, color='orange', linestyle='--', alpha=0.7, label='良好目标 (1.6)')
                    ax.axhline(y=1.8, color='red', linestyle='--', alpha=0.7, label='警戒线 (1.8)')
                    ax.legend(prop=font_prop)
                else:
                    ax.axhline(y=1.5, color='green', linestyle='--', alpha=0.7, label='Excellent (1.5)')
                    ax.axhline(y=1.6, color='orange', linestyle='--', alpha=0.7, label='Good (1.6)')
                    ax.axhline(y=1.8, color='red', linestyle='--', alpha=0.7, label='Warning (1.8)')
                    ax.legend()
                st.pyplot(fig)
            
            # PUE统计
            valid_pue = [x for x in all_data['PUE'] if x != 0]
            latest_pue, avg_pue = valid_pue[-1], np.mean(valid_pue)
            
            if st.session_state.is_mobile:
                col1, col2 = st.columns(2)
                col3, col4 = st.columns(2)
            else:
                col1, col2, col3, col4 = st.columns(4)
                
            col1.metric("最新PUE", f"{latest_pue:.3f}")
            col2.metric("平均PUE", f"{avg_pue:.3f}")
            col3.metric("最低PUE", f"{np.min(valid_pue):.3f}")
            col4.metric("最高PUE", f"{np.max(valid_pue):.3f}")
            
            # 评级
            st.subheader("📈 PUE能效评级")
            if latest_pue < 1.5:
                st.success("🎉 优秀 - 能效表现卓越")
            elif latest_pue < 1.6:
                st.info("👍 良好 - 能效表现良好")
            elif latest_pue < 1.8:
                st.warning("⚠️ 一般 - 有改进空间")
            else:
                st.error("❌ 较差 - 需要优化能效")
        else:
            st.warning("暂无PUE数据")
    
    else:
        st.info("⏳ 数据加载中，请稍候...")

elif page == "🎈 氢气传感器":
    st.title("🎈 氢气浓度监控")
    
    if st.session_state.data_loaded and st.session_state.all_data:
        all_data = st.session_state.all_data
        
        if all_data['hydr'] and any(x != 0 for x in all_data['hydr']):
            # 氢气图表
            fig, has_data = plot_recent_data(all_data['time'], {'氢气浓度': all_data['hydr']}, '氢气浓度监测 (最近数据)', '氢气浓度 (ppm)', colors=['purple'], 
                                           recent_points=8 if st.session_state.is_mobile else 12)
            if has_data:
                ax = fig.axes[0]
                font_prop = get_font_properties()
                if font_prop:
                    ax.axhline(y=50, color='green', linestyle='--', alpha=0.7, label='安全阈值 (50ppm)')
                    ax.legend(prop=font_prop)
                else:
                    ax.axhline(y=50, color='green', linestyle='--', alpha=0.7, label='Safety Threshold (50ppm)')
                    ax.legend()
                st.pyplot(fig)
            
            # 氢气统计
            valid_hydr = [x for x in all_data['hydr'] if x != 0]
            latest_hydr, avg_hydr = valid_hydr[-1], np.mean(valid_hydr)
            
            if st.session_state.is_mobile:
                col1, col2 = st.columns(2)
                col3 = st.columns(1)[0]
            else:
                col1, col2, col3 = st.columns(3)
                
            col1.metric("最新浓度", f"{latest_hydr:.1f}ppm")
            col2.metric("平均浓度", f"{avg_hydr:.1f}ppm")
            col3.metric("最高浓度", f"{np.max(valid_hydr):.1f}ppm")
            
            # 安全状态
            st.subheader("🛡️ 安全状态")
            if latest_hydr < 50:
                st.success("✅ 安全 - 氢气浓度在安全范围内")
            else:
                st.warning("⚠️ 注意 - 氢气浓度超过安全阈值")
        else:
            st.warning("暂无氢气浓度数据")
    
    else:
        st.info("⏳ 数据加载中，请稍候...")