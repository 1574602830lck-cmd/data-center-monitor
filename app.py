import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
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
        # 强制查找当前目录的字体文件
        current_dir_fonts = ['SimHei.ttf', 'simhei.ttf']
        
        font_path = None
        for font_file in current_dir_fonts:
            if os.path.exists(font_file):
                font_path = os.path.abspath(font_file)
                break
        
        if not font_path:
            raise FileNotFoundError("未在当前目录找到 SimHei.ttf 字体文件")
        
        # 清除字体缓存并设置字体
        if hasattr(fm, '_rebuild'):
            fm._rebuild()
        
        font_prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = [font_prop.get_name()]
        plt.rcParams['font.sans-serif'] = [font_prop.get_name()]
        plt.rcParams['axes.unicode_minus'] = False
        
        return font_path
        
    except Exception as e:
        st.error(f"字体设置失败: {str(e)}")
        st.error("请确保 SimHei.ttf 文件在当前目录中")
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

# 设置页面
st.set_page_config(
    page_title="数据中心监控系统", 
    page_icon="🏢", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 精简的CSS样式 - 专注移动端适配
st.markdown("""
<style>
/* 隐藏Streamlit默认元素 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* 移除顶部空白 */
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

/* 移动端适配 */
@media (max-width: 768px) {
    .main-header {
        font-size: 1.5em !important;
        padding: 10px !important;
    }
    
    .stats-card {
        padding: 12px !important;
        margin-bottom: 8px !important;
    }
    
    .stats-card .value {
        font-size: 1.3em !important;
    }
    
    .stats-card h3 {
        font-size: 0.8em !important;
    }
    
    /* 移动端按钮调整 - 更小的按钮 */
    .stButton button {
        font-size: 10px !important;
        padding: 4px 6px !important;
        margin: 1px !important;
        height: auto !important;
        min-height: 28px !important;
    }
    
    /* 移动端列布局 */
    .mobile-stack {
        flex-direction: column;
    }
}

/* 基础卡片样式 */
.stats-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    padding: 15px;
    color: white;
    margin-bottom: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.stats-card h3 {
    color: white;
    font-size: 0.8em;
    margin-bottom: 8px;
    opacity: 0.9;
}

.stats-card .value {
    font-size: 1.5em;
    font-weight: bold;
    margin-bottom: 5px;
}

.stats-card .subtitle {
    font-size: 0.7em;
    opacity: 0.8;
}

/* 进度条样式 */
.progress-container {
    background: rgba(255,255,255,0.2);
    border-radius: 8px;
    height: 4px;
    margin-top: 6px;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    border-radius: 8px;
    background: linear-gradient(90deg, #00d26a, #00b8d9);
}

/* 数据质量指示器 */
.data-quality {
    display: flex;
    align-items: center;
    margin-top: 8px;
    font-size: 0.7em;
}

.quality-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    margin-right: 4px;
}

.quality-excellent { background-color: #00d26a; }
.quality-good { background-color: #00b8d9; }
.quality-fair { background-color: #ffab00; }
.quality-poor { background-color: #ff5630; }

/* 更小的按钮样式 */
.compact-button {
    font-size: 11px !important;
    padding: 3px 8px !important;
    margin: 1px !important;
}

/* 紧凑的区域选择布局 */
.area-selector {
    gap: 4px !important;
}

/* 更小的图表容器 */
.small-chart {
    margin: 0;
    padding: 0;
}
</style>
""", unsafe_allow_html=True)

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

# 初始化温度页面区域选择状态
if 'temp_areas' not in st.session_state:
    areas = ['主机房', '冷通道', '电池间', '运营间', '配电间']
    selected_areas = random.sample(areas, 2)
    st.session_state.temp_areas = {area: (area in selected_areas) for area in areas}

# 初始化湿度页面区域选择状态
if 'hum_areas' not in st.session_state:
    areas = ['主机房', '冷通道', '电池间', '运营间', '配电间']
    selected_areas = random.sample(areas, 2)
    st.session_state.hum_areas = {area: (area in selected_areas) for area in areas}

# 自动加载数据
if not st.session_state.data_loaded:
    with st.spinner("🔄 正在从GitHub加载数据..."):
        all_data, success = load_data_from_github()
        if success and all_data:
            st.session_state.all_data = all_data
            st.session_state.data_loaded = True

# 图表绘制函数 - 更小的图表尺寸
def plot_recent_data(time_data, data_dict, title, ylabel, colors=None, recent_points=8, figsize=(4, 2)):
    if colors is None:
        colors = ['red', 'blue', 'green', 'orange', 'purple']
    
    font_prop = get_font_properties()
    
    # 使用传入的图表尺寸
    fig_width, fig_height = figsize
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    has_data = False
    
    for i, (label, data) in enumerate(data_dict.items()):
        if data and any(x != 0 for x in data):
            valid_data = [x for x in data if x != 0]
            valid_times = [time_data[i] for i, x in enumerate(data) if x != 0]
            
            if len(valid_data) > recent_points:
                valid_data = valid_data[-recent_points:]
                valid_times = valid_times[-recent_points:]
            
            if valid_data:
                ax.plot(valid_times, valid_data, label=label, color=colors[i % len(colors)], 
                       linewidth=1.0, marker='o', markersize=1.2)  # 减小线条和标记大小
                has_data = True
    
    if has_data:
        # 更小的字体大小
        title_size = 8
        label_size = 6
        legend_size = 5
        tick_size = 5
        
        if font_prop:
            ax.set_title(title, fontproperties=font_prop, fontsize=title_size, fontweight='bold')
            ax.set_ylabel(ylabel, fontproperties=font_prop, fontsize=label_size)
            ax.set_xlabel('时间', fontproperties=font_prop, fontsize=label_size)
            ax.legend(prop=font_prop, fontsize=legend_size, loc='upper right')
            plt.xticks(rotation=45, fontproperties=font_prop, fontsize=tick_size)
        else:
            ax.set_title(title, fontsize=title_size, fontweight='bold')
            ax.set_ylabel(ylabel, fontsize=label_size)
            ax.set_xlabel('Time', fontsize=label_size)
            ax.legend(fontsize=legend_size, loc='upper right')
            plt.xticks(rotation=45, fontsize=tick_size)
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig, True
    return None, False

# 检测移动端 - 简化版本
def is_mobile():
    """检测是否为移动端"""
    return False  # 统一布局，不再区分移动端和桌面端

# 设置移动端状态
st.session_state.is_mobile = is_mobile()

# 页面路由
if page == "📊 主界面":
    st.title("数据中心综合监控系统")
    
    if st.session_state.data_loaded and st.session_state.all_data:
        all_data = st.session_state.all_data
        
        # 关键指标 - 统一使用2x2布局
        st.subheader("📈 关键指标概览")
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        
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
        
        # 数据统计
        st.subheader("📊 数据质量分析")
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        
        with col1:
            total_datasets = len(all_data) - 1
            valid_datasets = sum(1 for key in all_data if key != 'time' and any(x != 0 for x in all_data[key]))
            completeness_rate = (valid_datasets / total_datasets) * 100
            
            st.markdown(f"""
            <div class="stats-card">
                <h3>📋 数据完整性</h3>
                <div class="value">{completeness_rate:.1f}%</div>
                <div class="subtitle">{valid_datasets}/{total_datasets} 数据集</div>
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
            if all_data['time'] and len(all_data['time']) > 0:
                latest_date = all_data['time'][-1]
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
        
        # 图表预览 - 一行显示两张图
        st.subheader("📈 数据趋势预览")
        
        col1, col2 = st.columns(2)
        
        with col1:
            temp_dict = {'主机房': all_data['ZJFTemp'], '冷通道': all_data['LTDTemp']}
            fig, has_data = plot_recent_data(all_data['time'], temp_dict, '温度趋势', '温度 (℃)', 
                                           recent_points=6, figsize=(3.5, 2))
            if has_data:
                st.pyplot(fig)
            else:
                st.info("暂无温度数据")
        
        with col2:
            if all_data['PUE'] and any(x != 0 for x in all_data['PUE']):
                pue_dict = {'PUE': all_data['PUE']}
                fig, has_data = plot_recent_data(all_data['time'], pue_dict, 'PUE趋势', 'PUE值', 
                                               colors=['blue'], recent_points=6, figsize=(3.5, 2))
                if has_data:
                    ax = fig.axes[0]
                    font_prop = get_font_properties()
                    if font_prop:
                        ax.axhline(y=1.5, color='green', linestyle='--', alpha=0.5, label='目标值 1.5')
                        ax.legend(prop=font_prop, fontsize=4)
                    else:
                        ax.axhline(y=1.5, color='green', linestyle='--', alpha=0.5, label='Target 1.5')
                        ax.legend(fontsize=4)
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
        
        # 区域选择 - 使用3列布局，更紧凑
        st.subheader("📍 选择监控区域")
        areas = ['主机房', '冷通道', '电池间', '运营间', '配电间']
        
        # 使用3列布局，按钮更紧凑
        cols = st.columns(3)
        for i, area in enumerate(areas):
            with cols[i % 3]:
                if st.button(area, key=f"btn_{area}", use_container_width=True,
                            type="primary" if st.session_state.temp_areas[area] else "secondary"):
                    st.session_state.temp_areas[area] = not st.session_state.temp_areas[area]
                    st.rerun()
        
        selected = [area for area, selected in st.session_state.temp_areas.items() if selected]
        if selected:
            st.info(f"已选择: {', '.join(selected)}")
        else:
            st.warning("请至少选择一个监控区域")
        
        # 温度图表 - 更小的图表
        temp_dict = {}
        area_mapping = {
            '主机房': 'ZJFTemp', '冷通道': 'LTDTemp', '电池间': 'DCJTemp',
            '运营间': 'YYJTemp', '配电间': 'PDJTemp'
        }
        
        for area in areas:
            if st.session_state.temp_areas[area]:
                data_key = area_mapping[area]
                temp_dict[area] = all_data[data_key]
        
        fig, has_data = plot_recent_data(all_data['time'], temp_dict, '数据中心温度监控', '温度 (℃)', 
                                       recent_points=6, figsize=(5, 2.2))
        if has_data:
            st.pyplot(fig)
        else:
            st.warning("所选区域暂无温度数据")
        
        # 温度统计
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
                    col1, col2 = st.columns(2)
                    col3, col4 = st.columns(2)
                    
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
        
        # 区域选择 - 使用3列布局，更紧凑
        st.subheader("📍 选择监控区域")
        areas = ['主机房', '冷通道', '电池间', '运营间', '配电间']
        
        # 使用3列布局，按钮更紧凑
        cols = st.columns(3)
        for i, area in enumerate(areas):
            with cols[i % 3]:
                if st.button(area, key=f"hum_btn_{area}", use_container_width=True,
                            type="primary" if st.session_state.hum_areas[area] else "secondary"):
                    st.session_state.hum_areas[area] = not st.session_state.hum_areas[area]
                    st.rerun()
        
        selected = [area for area, selected in st.session_state.hum_areas.items() if selected]
        if selected:
            st.info(f"已选择: {', '.join(selected)}")
        else:
            st.warning("请至少选择一个监控区域")
        
        # 湿度图表 - 更小的图表
        hum_dict = {}
        area_mapping = {
            '主机房': 'ZJFHum', '冷通道': 'LTDHum', '电池间': 'DCJHum',
            '运营间': 'YYJHum', '配电间': 'PDJHum'
        }
        
        for area in areas:
            if st.session_state.hum_areas[area]:
                data_key = area_mapping[area]
                hum_dict[area] = all_data[data_key]
        
        fig, has_data = plot_recent_data(all_data['time'], hum_dict, '数据中心湿度监控', '湿度 (%)', 
                                       recent_points=6, figsize=(5, 2.2))
        if has_data:
            st.pyplot(fig)
        else:
            st.warning("所选区域暂无湿度数据")
        
        # 湿度统计
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
                    col1, col2 = st.columns(2)
                    col3, col4 = st.columns(2)
                    
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

elif page == "⚡ PUE指标":
    st.title("⚡ PUE能效指标监控")
    
    if st.session_state.data_loaded and st.session_state.all_data:
        all_data = st.session_state.all_data
        
        if all_data['PUE'] and any(x != 0 for x in all_data['PUE']):
            # PUE图表 - 更小的图表
            fig, has_data = plot_recent_data(all_data['time'], {'PUE': all_data['PUE']}, 'PUE能效指标', 'PUE值', 
                                           colors=['blue'], recent_points=6, figsize=(5, 2.2))
            if has_data:
                ax = fig.axes[0]
                font_prop = get_font_properties()
                if font_prop:
                    ax.axhline(y=1.5, color='green', linestyle='--', alpha=0.7, label='优秀目标 (1.5)')
                    ax.axhline(y=1.6, color='orange', linestyle='--', alpha=0.7, label='良好目标 (1.6)')
                    ax.axhline(y=1.8, color='red', linestyle='--', alpha=0.7, label='警戒线 (1.8)')
                    ax.legend(prop=font_prop, fontsize=5)
                else:
                    ax.axhline(y=1.5, color='green', linestyle='--', alpha=0.7, label='Excellent (1.5)')
                    ax.axhline(y=1.6, color='orange', linestyle='--', alpha=0.7, label='Good (1.6)')
                    ax.axhline(y=1.8, color='red', linestyle='--', alpha=0.7, label='Warning (1.8)')
                    ax.legend(fontsize=5)
                st.pyplot(fig)
            
            # PUE统计
            valid_pue = [x for x in all_data['PUE'] if x != 0]
            latest_pue, avg_pue = valid_pue[-1], np.mean(valid_pue)
            
            col1, col2 = st.columns(2)
            col3, col4 = st.columns(2)
                
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
            # 氢气图表 - 更小的图表
            fig, has_data = plot_recent_data(all_data['time'], {'氢气浓度': all_data['hydr']}, '氢气浓度监测', '氢气浓度 (ppm)', 
                                           colors=['purple'], recent_points=6, figsize=(5, 2.2))
            if has_data:
                ax = fig.axes[0]
                font_prop = get_font_properties()
                if font_prop:
                    ax.axhline(y=50, color='green', linestyle='--', alpha=0.7, label='安全阈值 (50ppm)')
                    ax.legend(prop=font_prop, fontsize=5)
                else:
                    ax.axhline(y=50, color='green', linestyle='--', alpha=0.7, label='Safety Threshold (50ppm)')
                    ax.legend(fontsize=5)
                st.pyplot(fig)
            
            # 氢气统计
            valid_hydr = [x for x in all_data['hydr'] if x != 0]
            latest_hydr, avg_hydr = valid_hydr[-1], np.mean(valid_hydr)
            
            col1, col2 = st.columns(2)
            col3 = st.columns(1)[0]
                
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