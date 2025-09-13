# Material Flow Warnings and Bottleneck Analysis
if plant.material_flow_warnings or plant.bottlenecks:
    st.subheader("⚠️ Material Flow Analysis")
    
    # Material Flow Warnings
    if plant.material_flow_warnings:
        st.error("**Material Flow Warnings Detected:**")
        
        for warning in plant.material_flow_warnings:
            severity_color = {
                'Critical': '🔴',
                'High': '🟠', 
                'Moderate': '🟡'
            }.get(warning['severity'], '🔵')
            
            with st.expander(f"{severity_color} {warning['severity']} - {warning['process_type'].title()} {warning['stage']} Capacity Issue"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Required Material", f"{warning['required_mass']:.1f} t/h")
                    st.metric("Available Material", f"{warning['available_mass']:.1f} t/h")
                with col2:
                    st.metric("Material Shortage", f"{warning['shortage']:.1f} t/h")
                    st.metric("Shortage Percentage", f"{warning['shortage_percent']:.1f}%")
                with col3:
                    st.write("**Recommended Actions:**")
                    if warning['shortage_percent'] > 50:
                        st.write("- 🔧 Immediate equipment upgrade required")
                        st.write("- ⚡ Consider parallel processing units")
                        st.write("- 📉 Reduce upstream feed rate")
                    elif warning['shortage_percent'] > 25:
                        st.write("- 🔧 Schedule equipment maintenance")
                        st.write("- ⚙️ Optimize process parameters")
                        st.write("- 📊 Monitor closely for deterioration")
                    else:
                        st.write("- 👀 Monitor process performance")
                        st.write("- 🛠️ Plan preventive maintenance")
    
    # Process Bottlenecks
    if plant.bottlenecks:
        st.warning("**Process Bottlenecks Identified:**")
        
        for bottleneck in plant.bottlenecks:
            with st.expander(f"🚧 {bottleneck['process']} Process - {bottleneck['stage'].title()} Bottleneck"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Limiting Throughput", f"{bottleneck['limiting_throughput']:.1f} t/h")
                    if 'upstream_capacity' in bottleneck:
                        st.metric("Upstream Capacity", f"{bottleneck['upstream_capacity']:.1f} t/h")
                    else:
                        st.metric("Feed Rate", f"{bottleneck['feed_rate']:.1f} t/h")
                with col2:
                    st.metric("Efficiency Loss", f"{bottleneck['efficiency_loss']:.1f}%")
                    potential_gain = bottleneck.get('upstream_capacity', bottleneck.get('feed_rate', 0)) - bottleneck['limiting_throughput']
                    st.metric("Potential Throughput Gain", f"{potential_gain:.1f} t/h")
                with col3:
                    st.write("**Optimization Opportunities:**")
                    if bottleneck['stage'] == 'grinding':
                        st.write("- ⚙️ Increase mill capacity")
                        st.write("- 🔧 Optimize grinding parameters")
                        st.write("- 📈 Add parallel grinding circuit")
                    elif bottleneck['stage'] == 'flotation':
                        st.write("- 🧪 Optimize reagent dosing")
                        st.write("- ⏱️ Increase flotation residence time")
                        st.write("- 🔄 Add flotation cells")
                    else:
                        st.write("- 🔧 Equipment capacity upgrade")
                        st.write("- ⚙️ Process parameter optimization")
                        st.write("- 📊 Operational efficiency improvement")

# Capacity Utilization Analysis
if 'oxide' in plant.stage_results or 'sulphide' in plant.stage_results:
    st.subheader("📊 Equipment Capacity Utilization")
    
    capacity_data = []
    
    if 'oxide' in plant.stage_results:
        oxide_stages = plant.stage_results['oxide']
        
        # Calculate capacity utilization for each oxide stage
        for stage_name, stage_data in oxide_stages.items():
            if 'capacity' in stage_data and stage_name != 'feed':
                utilization = (stage_data['mass'] / stage_data['capacity']) * 100
                capacity_data.append({
                    'Process': 'Oxide',
                    'Stage': stage_name.title(),
                    'Actual Throughput (t/h)': stage_data['mass'],
                    'Design Capacity (t/h)': stage_data['capacity'],
                    'Utilization (%)': utilization,
                    'Available Capacity (t/h)': stage_data['capacity'] - stage_data['mass'],
                    'Status': 'Overloaded' if utilization > 100 else 'Critical' if utilization > 90 else 'Normal'
                })
    
    if 'sulphide' in plant.stage_results:
        sulphide_stages = plant.stage_results['sulphide']
        
        # Calculate capacity utilization for each sulphide stage
        for stage_name, stage_data in sulphide_stages.items():
            if 'capacity' in stage_data and stage_name != 'feed':
                if stage_name in ['cu_flotation', 'ni_flotation']:
                    throughput = stage_data['concentrate_mass']
                else:
                    throughput = stage_data['mass']
                    
                utilization = (throughput / stage_data['capacity']) * 100
                capacity_data.append({
                    'Process': 'Sulphide',
                    'Stage': stage_name.replace('_', ' ').title(),
                    'Actual Throughput (t/h)': throughput,
                    'Design Capacity (t/h)': stage_data['capacity'],
                    'Utilization (%)': utilization,
                    'Available Capacity (t/h)': stage_data['capacity'] - throughput,
                    'Status': 'Overloaded' if utilization > 100 else 'Critical' if utilization > 90 else 'Normal'
                })
    
    if capacity_data:
        capacity_df = pd.DataFrame(capacity_data)
        
        # Color code the dataframe based on status
        def color_status(val):
            if val == 'Overloaded':
                return 'background-color: #ffebee; color: #c62828'
            elif val == 'Critical':
                return 'background-color: #fff3e0; color: #ef6c00'
            else:
                return 'background-color: #e8f5e8; color: #2e7d32'
        
        styled_df = capacity_df.style.applymap(color_status, subset=['Status'])
        st.dataframe(styled_df, use_container_width=True)
        
        # Capacity utilization chart
        fig_capacity = px.bar(capacity_df, x='Stage', y='Utilization (%)', 
                             color='Process', barmode='group',
                             title="Equipment Capacity Utilization by Stage")
        fig_capacity.add_hline(y=100, line_dash="dash", line_color="red", 
                              annotation_text="Maximum Capacity")
        fig_capacity.add_hline(y=90, line_dash="dash", line_color="orange", 
                              annotation_text="Critical Threshold (90%)")
        st.plotly_chart(fig_capacity, use_container_width=True)
        
        # Summary metrics
        st.write("**Capacity Utilization Summary:**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            avg_utilization = capacity_df['Utilization (%)'].mean()
            st.metric("Average Utilization", f"{avg_utilization:.1f}%")
        with col2:
            overloaded_count = len(capacity_df[capacity_df['Status'] == 'Overloaded'])
            st.metric("Overloaded Stages", f"{overloaded_count}")
        with col3:
            critical_count = len(capacity_df[capacity_df['Status'] == 'Critical'])
            st.metric("Critical Stages", f"{critical_count}")
        with col4:
            total_spare_capacity = capacity_df['Available Capacity (t/h)'].sum()
            st.metric("Total Spare Capacity", f"{total_spare_capacity:.1f} t/h")

else:
    # Success message when no issues detected
    st.success("✅ **Material Flow Validation: All Clear**")
    st.write("No material flow warnings or bottlenecks detected. All process stages have sufficient capacity to handle current throughput rates.")

# Display current throughput rates
st.subheader("⚡ Current Operating Parameters")
col1, col2, col3 = st.columns(3)
with col1:
    if feed_type in ["Oxide Feed", "Both Feeds"]:
        st.metric("Oxide Feed Rate", f"{oxide_feed_rate:.0f} t/h")
with col2:
    if feed_type in ["Sulphide Feed", "Both Feeds"]:
        st.metric("Sulphide Feed Rate", f"{sulphide_feed_rate:.0f} t/h")
with col3:
    total_throughput = 0
    if feed_type in ["Oxide Feed", "Both Feeds"]:
        total_throughput += oxide_feed_rate
    if feed_type in ["Sulphide Feed", "Both Feeds"]:
        total_throughput += sulphide_feed_rate
    st.metric("Total Feed Rate", f"{total_throughput:.0f} t/h")

# Stage-by-Stage Process Analysis
if 'oxide' in plant.stage_results or 'sulphide' in plant.stage_results:
    st.subheader("🔄 Stage-by-Stage Process Analysis")
    
    # Oxide process stages
    if 'oxide' in plant.stage_results:
        st.write("**Oxide Process Flow:**")
        oxide_stages = plant.stage_results['oxide']
        
        # Create detailed oxide process table
        oxide_process_data = {
            'Process Stage': ['Feed', 'After Sizing', 'After Grinding', 'Leach Solution', 'Tailings'],
            'Mass (t/h)': [
                oxide_stages['feed']['mass'],
                oxide_stages['sizing']['mass'],
                oxide_stages['grinding']['mass'],
                oxide_stages['leaching']['mass'],
                oxide_stages['tailings']['mass']
            ],
            'Pd Content (kg/h)': [
                oxide_stages['feed']['pd'],
                oxide_stages['sizing']['pd'],
                oxide_stages['grinding']['pd'],
                oxide_stages['leaching']['pd_recovered'],
                oxide_stages['tailings']['pd']
            ],
            'Au Content (kg/h)': [
                oxide_stages['feed']['au'],
                oxide_stages['sizing']['au'],
                oxide_stages['grinding']['au'],
                oxide_stages['leaching']['au_recovered'],
                oxide_stages['tailings']['au']
            ],
            'Stage Recovery (%)': [
                100.0,
                (oxide_stages['sizing']['mass'] / oxide_stages['feed']['mass']) * 100,
                (oxide_stages['grinding']['mass'] / oxide_stages['sizing']['mass']) * 100,
                (oxide_stages['leaching']['mass'] / oxide_stages['grinding']['mass']) * 100,
                ((oxide_stages['grinding']['mass'] - oxide_stages['leaching']['mass']) / oxide_stages['grinding']['mass']) * 100
            ]
        }
        
        oxide_df = pd.DataFrame(oxide_process_data)
        st.dataframe(oxide_df, use_container_width=True)
        
        # Process losses breakdown
        st.write("**Oxide Process Losses:**")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Sizing Losses", f"{oxide_stages['sizing']['losses']:.1f} t/h")
        with col2:
            st.metric("Grinding Losses", f"{oxide_stages['grinding']['losses']:.1f} t/h")

    # Sulphide process stages
    if 'sulphide' in plant.stage_results:
        st.write("**Sulphide Process Flow:**")
        sulphide_stages = plant.stage_results['sulphide']
        
        # Main process stages table
        sulphide_process_data = {
            'Process Stage': ['Feed', 'After Crushing', 'After Grinding', 'Cu Concentrate', 'Ni Concentrate', 'Flotation Tailings'],
            'Mass (t/h)': [
                sulphide_stages['feed']['mass'],
                sulphide_stages['crushing']['mass'],
                sulphide_stages['grinding']['mass'],
                sulphide_stages['cu_flotation']['concentrate_mass'],
                sulphide_stages['ni_flotation']['concentrate_mass'],
                sulphide_stages['tailings']['mass']
            ],
            'Cu Content (kg/h)': [
                sulphide_stages['feed']['cu'],
                sulphide_stages['crushing']['cu'],
                sulphide_stages['grinding']['cu'],
                sulphide_stages['cu_flotation']['cu'],
                0,
                0
            ],
            'Ni Content (kg/h)': [
                sulphide_stages['feed']['ni'],
                sulphide_stages['crushing']['ni'],
                sulphide_stages['grinding']['ni'],
                0,
                sulphide_stages['ni_flotation']['ni'],
                0
            ],
            'Stage Recovery (%)': [
                100.0,
                (sulphide_stages['crushing']['mass'] / sulphide_stages['feed']['mass']) * 100,
                (sulphide_stages['grinding']['mass'] / sulphide_stages['crushing']['mass']) * 100,
                (sulphide_stages['cu_flotation']['concentrate_mass'] / sulphide_stages['grinding']['mass']) * 100,
                (sulphide_stages['ni_flotation']['concentrate_mass'] / (sulphide_stages['grinding']['mass'] - sulphide_stages['cu_flotation']['concentrate_mass'])) * 100,
                (sulphide_stages['tailings']['mass'] / sulphide_stages['grinding']['mass']) * 100
            ]
        }
        
        sulphide_df = pd.DataFrame(sulphide_process_data)
        st.dataframe(sulphide_df, use_container_width=True)
        
        # PGM distribution analysis
        st.write("**PGM Distribution Through Process:**")
        pgm_distribution_data = {
            'Metal': ['Pd', 'Pt', 'Au'],
            'Feed (kg/h)': [
                sulphide_stages['feed']['pd'],
                sulphide_stages['feed']['pt'],
                sulphide_stages['feed']['au']
            ],
            'To Cu Concentrate (kg/h)': [
                sulphide_stages['cu_flotation']['pd'],
                sulphide_stages['cu_flotation']['pt'],
                sulphide_stages['cu_flotation']['au']
            ],
            'To Ni Concentrate (kg/h)': [
                sulphide_stages['ni_flotation']['pd'],
                sulphide_stages['ni_flotation']['pt'],
                sulphide_stages['ni_flotation']['au']
            ],
            'Final Recovery (kg/h)': [
                sulphide_stages['final_products']['pd'],
                sulphide_stages['final_products']['pt'],
                sulphide_stages['final_products']['au']
            ],
            'Overall Recovery (%)': [
                (sulphide_stages['final_products']['pd'] / sulphide_stages['feed']['pd']) * 100 if sulphide_stages['feed']['pd'] > 0 else 0,
                (sulphide_stages['final_products']['pt'] / sulphide_stages['feed']['pt']) * 100 if sulphide_stages['feed']['pt'] > 0 else 0,
                (sulphide_stages['final_products']['au'] / sulphide_stages['feed']['au']) * 100 if sulphide_stages['feed']['au'] > 0 else 0
            ]
        }
        
        pgm_df = pd.DataFrame(pgm_distribution_data)
        st.dataframe(pgm_df, use_container_width=True)
        
        # Process losses breakdown
        st.write("**Sulphide Process Losses:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Crushing Losses", f"{sulphide_stages['crushing']['losses']:.1f} t/h")
        with col2:
            st.metric("Grinding Losses", f"{sulphide_stages['grinding']['losses']:.1f} t/h")
        with col3:
            total_losses = sulphide_stages['crushing']['losses'] + sulphide_stages['grinding']['losses']
            st.metric("Total Process Losses", f"{total_losses:.1f} t/h")

# Process efficiency analysis
st.subheader("📈 Process Efficiency Analysis")

if feed_type in ["Oxide Feed", "Both Feeds"] and 'oxide' in plant.stage_results:
    st.write("**Oxide Process Efficiencies:**")
    oxide_stages = plant.stage_results['oxide']
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        sizing_eff = (oxide_stages['sizing']['mass'] / oxide_stages['feed']['mass']) * 100
        st.metric("Sizing Efficiency", f"{sizing_eff:.1f}%")
    with col2:
        grinding_eff = (oxide_stages['grinding']['mass'] / oxide_stages['sizing']['mass']) * 100
        st.metric("Grinding Efficiency", f"{grinding_eff:.1f}%")
    with col3:
        pd_recovery_eff = (oxide_stages['leaching']['pd_recovered'] / oxide_stages['feed']['pd']) * 100 if oxide_stages['feed']['pd'] > 0 else 0
        st.metric("Pd Recovery", f"{pd_recovery_eff:.1f}%")
    with col4:
        au_recovery_eff = (oxide_stages['leaching']['au_recovered'] / oxide_stages['feed']['au']) * 100 if oxide_stages['feed']['au'] > 0 else 0
        st.metric("Au Recovery", f"{au_recovery_eff:.1f}%")

if feed_type in ["Sulphide Feed", "Both Feeds"] and 'sulphide' in plant.stage_results:
    st.write("**Sulphide Process Efficiencies:**")
    sulphide_stages = plant.stage_results['sulphide']
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        crushing_eff = (sulphide_stages['crushing']['mass'] / sulphide_stages['feed']['mass']) * 100
        st.metric("Crushing Efficiency", f"{crushing_eff:.1f}%")
    with col2:
        grinding_eff = (sulphide_stages['grinding']['mass'] / sulphide_stages['crushing']['mass']) * 100
        st.metric("Grinding Efficiency", f"{grinding_eff:.1f}%")
    with col3:
        cu_recovery_eff = (sulphide_stages['final_products']['cu'] / sulphide_stages['feed']['cu']) * 100 if sulphide_stages['feed']['cu'] > 0 else 0
        st.metric("Cu Recovery", f"{cu_recovery_eff:.1f}%")
    with col4:
        ni_recovery_eff = (sulphide_stages['final_products']['ni'] / sulphide_stages['feed']['ni']) * 100 if sulphide_stages['feed']['ni'] > 0 else 0
        st.metric("Ni Recovery", f"{ni_recovery_eff:.1f}%")
    with col5:
        overall_mass_recovery = ((sulphide_stages['cu_flotation']['concentrate_mass'] + sulphide_stages['ni_flotation']['concentrate_mass']) / sulphide_stages['feed']['mass']) * 100
        st.metric("Mass to Concentrates", f"{overall_mass_recovery:.1f}%")

# Display resultsimport streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="Metallurgical Plant Simulator",
    page_icon="⚒️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("⚒️ Metallurgical Plant Process Simulator")
st.markdown("Simulate the processing of oxide and sulphide feeds through a complete metallurgical plant")

# Sidebar for input parameters
st.sidebar.header("Feed Composition & Process Parameters")

# Feed selection
feed_type = st.sidebar.selectbox("Select Feed Type:", ["Oxide Feed", "Sulphide Feed", "Both Feeds"])

# Feed composition inputs
st.sidebar.subheader("Feed Composition (%)")
cu_grade = st.sidebar.slider("Copper (Cu)", 0.1, 5.0, 1.5, 0.1)
pd_grade = st.sidebar.slider("Palladium (Pd)", 0.01, 2.0, 0.8, 0.01)
pt_grade = st.sidebar.slider("Platinum (Pt)", 0.01, 2.0, 0.6, 0.01)
au_grade = st.sidebar.slider("Gold (Au)", 0.01, 1.0, 0.3, 0.01)
ni_grade = st.sidebar.slider("Nickel (Ni)", 0.1, 3.0, 1.2, 0.1) if feed_type in ["Sulphide Feed", "Both Feeds"] else 0
co_grade = st.sidebar.slider("Cobalt (Co)", 0.05, 1.0, 0.4, 0.05) if feed_type in ["Sulphide Feed", "Both Feeds"] else 0

# Process parameters
st.sidebar.subheader("Process Parameters")
throughput = st.sidebar.number_input("Throughput (tonnes/hour)", 10, 1000, 100, 10)
grinding_efficiency = st.sidebar.slider("Grinding Efficiency (%)", 70, 95, 85, 1)
flotation_recovery = st.sidebar.slider("Flotation Recovery (%)", 75, 95, 88, 1)
leaching_recovery = st.sidebar.slider("Leaching Recovery (%)", 85, 98, 92, 1)

# Recovery factors for different processes
crushing_loss = st.sidebar.slider("Crushing Loss (%)", 1, 5, 2, 1) / 100
sizing_loss = st.sidebar.slider("Sizing Loss (%)", 0.5, 3, 1, 0.5) / 100

class MetallurgicalPlant:
    def __init__(self, feed_composition, process_params):
        self.feed_composition = feed_composition
        self.process_params = process_params
        self.results = {}
        
    def process_oxide_feed(self):
        """Process oxide feed through sizing, grinding, and leaching"""
        feed_mass = self.process_params['throughput']
        
        # Sizing
        sizing_recovery = 1 - self.process_params['sizing_loss']
        sized_mass = feed_mass * sizing_recovery
        
        # Grinding
        grinding_eff = self.process_params['grinding_efficiency'] / 100
        ground_mass = sized_mass * grinding_eff
        
        # Leaching (75% Pd and 90% Au recovery as stated in diagram)
        leaching_rec = self.process_params['leaching_recovery'] / 100
        pd_recovered = self.feed_composition['Pd'] * ground_mass * 0.75 * leaching_rec / 100
        au_recovered = self.feed_composition['Au'] * ground_mass * 0.90 * leaching_rec / 100
        
        # Tailings to storage
        tailings_mass = ground_mass * (1 - leaching_rec)
        
        self.results['oxide'] = {
            'feed_mass': feed_mass,
            'sized_mass': sized_mass,
            'ground_mass': ground_mass,
            'pd_recovered': pd_recovered,
            'au_recovered': au_recovered,
            'tailings_mass': tailings_mass,
            'leach_solution_mass': ground_mass * leaching_rec
        }
        
    def process_sulphide_feed(self):
        """Process sulphide feed through crushing, grinding, flotation, and downstream processes"""
        feed_mass = self.process_params['throughput']
        
        # Crushing
        crushing_recovery = 1 - self.process_params['crushing_loss']
        crushed_mass = feed_mass * crushing_recovery
        
        # Grinding
        grinding_eff = self.process_params['grinding_efficiency'] / 100
        ground_mass = crushed_mass * grinding_eff
        
        # Copper Flotation
        cu_flotation_rec = self.process_params['flotation_recovery'] / 100
        cu_concentrate_mass = ground_mass * 0.25  # Typical concentrate yield
        cu_recovered = self.feed_composition['Cu'] * ground_mass * cu_flotation_rec / 100
        pd_in_cu_conc = self.feed_composition['Pd'] * cu_concentrate_mass * 0.6 / 100
        pt_in_cu_conc = self.feed_composition['Pt'] * cu_concentrate_mass * 0.6 / 100
        au_in_cu_conc = self.feed_composition['Au'] * cu_concentrate_mass * 0.6 / 100
        
        # Nickel-Iron Flotation
        ni_flotation_rec = cu_flotation_rec * 0.9  # Slightly lower recovery
        ni_concentrate_mass = (ground_mass - cu_concentrate_mass) * 0.3
        ni_recovered = self.feed_composition['Ni'] * ni_concentrate_mass * ni_flotation_rec / 100
        co_recovered = self.feed_composition['Co'] * ni_concentrate_mass * ni_flotation_rec / 100
        
        # Pressure Oxidation & Precipitation
        pressure_ox_recovery = 0.95
        cu_final = cu_recovered * pressure_ox_recovery
        pd_final = pd_in_cu_conc * pressure_ox_recovery
        pt_final = pt_in_cu_conc * pressure_ox_recovery
        au_final = au_in_cu_conc * pressure_ox_recovery
        
        # Ni-Co precipitation
        ni_final = ni_recovered * 0.92
        co_final = co_recovered * 0.92
        
        self.results['sulphide'] = {
            'feed_mass': feed_mass,
            'crushed_mass': crushed_mass,
            'ground_mass': ground_mass,
            'cu_concentrate_mass': cu_concentrate_mass,
            'ni_concentrate_mass': ni_concentrate_mass,
            'cu_recovered': cu_final,
            'pd_recovered': pd_final,
            'pt_recovered': pt_final,
            'au_recovered': au_final,
            'ni_recovered': ni_final,
            'co_recovered': co_final,
            'tailings_mass': ground_mass - cu_concentrate_mass - ni_concentrate_mass
        }
        
    def run_simulation(self):
        """Run the complete simulation"""
        if feed_type in ["Oxide Feed", "Both Feeds"]:
            self.process_oxide_feed()
        if feed_type in ["Sulphide Feed", "Both Feeds"]:
            self.process_sulphide_feed()

# Create plant instance and run simulation
feed_composition = {
    'Cu': cu_grade,
    'Pd': pd_grade,
    'Pt': pt_grade,
    'Au': au_grade,
    'Ni': ni_grade,
    'Co': co_grade
}

process_params = {
    'throughput': throughput,
    'grinding_efficiency': grinding_efficiency,
    'flotation_recovery': flotation_recovery,
    'leaching_recovery': leaching_recovery,
    'crushing_loss': crushing_loss,
    'sizing_loss': sizing_loss
}

plant = MetallurgicalPlant(feed_composition, process_params)
plant.run_simulation()

# Display scenario information
if production_scenario != "Custom":
    st.subheader(f"📋 {production_scenario} Overview")
    scenario_data = scenarios[production_scenario]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Material Mined", f"{scenario_data['total_mined']} Mt")
        st.metric("3E Grade", f"{scenario_data['3E_grade']} g/t")
    with col2:
        st.metric("Total Processed", f"{scenario_data['total_processed']} Mt")
        st.metric("Copper Grade", f"{scenario_data['cu_grade']}%")
    with col3:
        st.metric("Sulphide Mine Life", f"{scenario_data['mine_life_sulphide']} years")
        st.metric("Nickel Grade", f"{scenario_data['ni_grade']}%")
    with col4:
        st.metric("Oxide Mine Life", f"{scenario_data['mine_life_oxide']} years")
        st.metric("Cobalt Grade", f"{scenario_data['co_grade']}%")

# Display current throughput rates
st.subheader("⚡ Current Operating Parameters")
col1, col2, col3 = st.columns(3)
with col1:
    if feed_type in ["Oxide Feed", "Both Feeds"]:
        st.metric("Oxide Throughput", f"{oxide_throughput:.0f} t/h")
with col2:
    if feed_type in ["Sulphide Feed", "Both Feeds"]:
        st.metric("Sulphide Throughput", f"{sulphide_throughput:.0f} t/h")
with col3:
    total_throughput = 0
    if feed_type in ["Oxide Feed", "Both Feeds"]:
        total_throughput += oxide_throughput
    if feed_type in ["Sulphide Feed", "Both Feeds"]:
        total_throughput += sulphide_throughput
    st.metric("Total Throughput", f"{total_throughput:.0f} t/h")

# Display results
col1, col2 = st.columns(2)

if feed_type in ["Oxide Feed", "Both Feeds"] and 'oxide' in plant.results:
    with col1:
        st.subheader("🔄 Oxide Feed Processing Results")
        oxide_results = plant.results['oxide']
        
        # Mass balance table
        mass_balance_df = pd.DataFrame({
            'Process Step': ['Feed', 'After Sizing', 'After Grinding', 'Leach Solution', 'Tailings'],
            'Mass (t/h)': [
                oxide_results['feed_mass'],
                oxide_results['sized_mass'],
                oxide_results['ground_mass'],
                oxide_results['leach_solution_mass'],
                oxide_results['tailings_mass']
            ]
        })
        
        st.dataframe(mass_balance_df, use_container_width=True)
        
        # Metal recovery
        st.write("**Metal Recovery:**")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Palladium Recovery", f"{oxide_results['pd_recovered']:.2f} kg/h")
        with col_b:
            st.metric("Gold Recovery", f"{oxide_results['au_recovered']:.2f} kg/h")

if feed_type in ["Sulphide Feed", "Both Feeds"] and 'sulphide' in plant.results:
    with col2:
        st.subheader("⚡ Sulphide Feed Processing Results")
        sulphide_results = plant.results['sulphide']
        
        # Mass balance table
        mass_balance_df = pd.DataFrame({
            'Process Step': ['Feed', 'After Crushing', 'After Grinding', 'Cu Concentrate', 'Ni Concentrate', 'Tailings'],
            'Mass (t/h)': [
                sulphide_results['feed_mass'],
                sulphide_results['crushed_mass'],
                sulphide_results['ground_mass'],
                sulphide_results['cu_concentrate_mass'],
                sulphide_results['ni_concentrate_mass'],
                sulphide_results['tailings_mass']
            ]
        })
        
        st.dataframe(mass_balance_df, use_container_width=True)
        
        # Metal recovery
        st.write("**Final Metal Production:**")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Copper", f"{sulphide_results['cu_recovered']:.2f} kg/h")
            st.metric("Palladium", f"{sulphide_results['pd_recovered']:.2f} kg/h")
        with col_b:
            st.metric("Platinum", f"{sulphide_results['pt_recovered']:.2f} kg/h")
            st.metric("Gold", f"{sulphide_results['au_recovered']:.2f} kg/h")
        with col_c:
            st.metric("Nickel", f"{sulphide_results['ni_recovered']:.2f} kg/h")
            st.metric("Cobalt", f"{sulphide_results['co_recovered']:.2f} kg/h")

# Process flow visualization
st.subheader("📊 Process Flow Visualization")

# Create flow chart data for visualization
if feed_type in ["Oxide Feed", "Both Feeds"] and 'oxide' in plant.results:
    fig_oxide = go.Figure()
    
    # Oxide process flow
    steps = ['Feed', 'Sizing', 'Grinding', 'Leaching', 'Tailings Storage']
    masses = [
        plant.results['oxide']['feed_mass'],
        plant.results['oxide']['sized_mass'],
        plant.results['oxide']['ground_mass'],
        plant.results['oxide']['leach_solution_mass'],
        plant.results['oxide']['tailings_mass']
    ]
    
    fig_oxide.add_trace(go.Scatter(
        x=list(range(len(steps))),
        y=masses,
        mode='lines+markers',
        name='Mass Flow',
        line=dict(color='orange', width=3),
        marker=dict(size=10)
    ))
    
    fig_oxide.update_layout(
        title="Oxide Feed Mass Flow Through Plant",
        xaxis_title="Process Step",
        yaxis_title="Mass (tonnes/hour)",
        xaxis=dict(tickmode='array', tickvals=list(range(len(steps))), ticktext=steps)
    )
    
    st.plotly_chart(fig_oxide, use_container_width=True)

if feed_type in ["Sulphide Feed", "Both Feeds"] and 'sulphide' in plant.results:
    fig_sulphide = go.Figure()
    
    # Sulphide process flow
    steps = ['Feed', 'Crushing', 'Grinding', 'Cu Flotation', 'Ni Flotation', 'Final Products']
    masses = [
        plant.results['sulphide']['feed_mass'],
        plant.results['sulphide']['crushed_mass'],
        plant.results['sulphide']['ground_mass'],
        plant.results['sulphide']['cu_concentrate_mass'],
        plant.results['sulphide']['ni_concentrate_mass'],
        plant.results['sulphide']['cu_recovered'] + plant.results['sulphide']['ni_recovered']
    ]
    
    fig_sulphide.add_trace(go.Scatter(
        x=list(range(len(steps))),
        y=masses,
        mode='lines+markers',
        name='Mass Flow',
        line=dict(color='blue', width=3),
        marker=dict(size=10)
    ))
    
    fig_sulphide.update_layout(
        title="Sulphide Feed Mass Flow Through Plant",
        xaxis_title="Process Step",
        yaxis_title="Mass (tonnes/hour)",
        xaxis=dict(tickmode='array', tickvals=list(range(len(steps))), ticktext=steps)
    )
    
    st.plotly_chart(fig_sulphide, use_container_width=True)

# Metal recovery comparison chart
st.subheader("🏆 Metal Recovery Summary")

if feed_type == "Both Feeds" and 'oxide' in plant.results and 'sulphide' in plant.results:
    # Combined recovery chart
    metals = ['Pd', 'Pt', 'Au', 'Cu', 'Ni', 'Co']
    oxide_recovery = [
        plant.results['oxide']['pd_recovered'],
        0,  # No Pt in oxide path
        plant.results['oxide']['au_recovered'],
        0, 0, 0  # No Cu, Ni, Co in oxide path
    ]
    sulphide_recovery = [
        plant.results['sulphide']['pd_recovered'],
        plant.results['sulphide']['pt_recovered'],
        plant.results['sulphide']['au_recovered'],
        plant.results['sulphide']['cu_recovered'],
        plant.results['sulphide']['ni_recovered'],
        plant.results['sulphide']['co_recovered']
    ]
    
    fig_recovery = go.Figure(data=[
        go.Bar(name='Oxide Feed', x=metals, y=oxide_recovery, marker_color='orange'),
        go.Bar(name='Sulphide Feed', x=metals, y=sulphide_recovery, marker_color='blue')
    ])
    
    fig_recovery.update_layout(
        title="Metal Recovery Comparison (kg/h)",
        xaxis_title="Metals",
        yaxis_title="Recovery (kg/h)",
        barmode='group'
    )
    
    st.plotly_chart(fig_recovery, use_container_width=True)

elif 'oxide' in plant.results:
    metals = ['Pd', 'Au']
    recovery = [plant.results['oxide']['pd_recovered'], plant.results['oxide']['au_recovered']]
    
    fig_recovery = px.bar(x=metals, y=recovery, title="Oxide Feed Metal Recovery (kg/h)",
                         color=metals, color_discrete_sequence=['orange', 'gold'])
    st.plotly_chart(fig_recovery, use_container_width=True)

elif 'sulphide' in plant.results:
    metals = ['Cu', 'Pd', 'Pt', 'Au', 'Ni', 'Co']
    recovery = [
        plant.results['sulphide']['cu_recovered'],
        plant.results['sulphide']['pd_recovered'],
        plant.results['sulphide']['pt_recovered'],
        plant.results['sulphide']['au_recovered'],
        plant.results['sulphide']['ni_recovered'],
        plant.results['sulphide']['co_recovered']
    ]
    
    fig_recovery = px.bar(x=metals, y=recovery, title="Sulphide Feed Metal Recovery (kg/h)",
                         color=metals, color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig_recovery, use_container_width=True)

# Economic analysis
st.subheader("💰 Economic Analysis")

# Metal prices (example values in USD/kg)
metal_prices = {
    'Cu': 8.5,
    'Pd': 32000,
    'Pt': 28000,
    'Au': 65000,
    'Ni': 18,
    'Co': 35
}

col1, col2, col3 = st.columns(3)

total_value_per_hour = 0

if 'oxide' in plant.results:
    oxide_value = (plant.results['oxide']['pd_recovered'] * metal_prices['Pd'] + 
                   plant.results['oxide']['au_recovered'] * metal_prices['Au'])
    total_value_per_hour += oxide_value
    with col1:
        st.metric("Oxide Feed Value", f"${oxide_value:,.0f}/hour")

if 'sulphide' in plant.results:
    sulphide_value = (plant.results['sulphide']['cu_recovered'] * metal_prices['Cu'] +
                      plant.results['sulphide']['pd_recovered'] * metal_prices['Pd'] +
                      plant.results['sulphide']['pt_recovered'] * metal_prices['Pt'] +
                      plant.results['sulphide']['au_recovered'] * metal_prices['Au'] +
                      plant.results['sulphide']['ni_recovered'] * metal_prices['Ni'] +
                      plant.results['sulphide']['co_recovered'] * metal_prices['Co'])
    total_value_per_hour += sulphide_value
    with col2:
        st.metric("Sulphide Feed Value", f"${sulphide_value:,.0f}/hour")

with col3:
    st.metric("Total Plant Value", f"${total_value_per_hour:,.0f}/hour")
    st.metric("Daily Revenue", f"${total_value_per_hour * 24:,.0f}/day")

# Material Flow Warnings and Bottleneck Analysis
if plant.material_flow_warnings or plant.bottlenecks:
    st.subheader("⚠️ Material Flow Analysis")
    
    # Material Flow Warnings
    if plant.material_flow_warnings:
        st.error("**Material Flow Warnings Detected:**")
        
        for warning in plant.material_flow_warnings:
            severity_color = {
                'Critical': '🔴',
                'High': '🟠', 
                'Moderate': '🟡'
            }.get(warning['severity'], '🔵')
            
            with st.expander(f"{severity_color} {warning['severity']} - {warning['process_type'].title()} {warning['stage']} Capacity Issue"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Required Material", f"{warning['required_mass']:.1f} t/h")
                    st.metric("Available Material", f"{warning['available_mass']:.1f} t/h")
                with col2:
                    st.metric("Material Shortage", f"{warning['shortage']:.1f} t/h")
                    st.metric("Shortage Percentage", f"{warning['shortage_percent']:.1f}%")
                with col3:
                    st.write("**Recommended Actions:**")
                    if warning['shortage_percent'] > 50:
                        st.write("- 🔧 Immediate equipment upgrade required")
                        st.write("- ⚡ Consider parallel processing units")
                        st.write("- 📉 Reduce upstream feed rate")
                    elif warning['shortage_percent'] > 25:
                        st.write("- 🔧 Schedule equipment maintenance")
                        st.write("- ⚙️ Optimize process parameters")
                        st.write("- 📊 Monitor closely for deterioration")
                    else:
                        st.write("- 👀 Monitor process performance")
                        st.write("- 🛠️ Plan preventive maintenance")
    
    # Process Bottlenecks
    if plant.bottlenecks:
        st.warning("**Process Bottlenecks Identified:**")
        
        for bottleneck in plant.bottlenecks:
            with st.expander(f"🚧 {bottleneck['process']} Process - {bottleneck['stage'].title()} Bottleneck"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Limiting Throughput", f"{bottleneck['limiting_throughput']:.1f} t/h")
                    if 'upstream_capacity' in bottleneck:
                        st.metric("Upstream Capacity", f"{bottleneck['upstream_capacity']:.1f} t/h")
                    else:
                        st.metric("Feed Rate", f"{bottleneck['feed_rate']:.1f} t/h")
                with col2:
                    st.metric("Efficiency Loss", f"{bottleneck['efficiency_loss']:.1f}%")
                    potential_gain = bottleneck.get('upstream_capacity', bottleneck.get('feed_rate', 0)) - bottleneck['limiting_throughput']
                    st.metric("Potential Throughput Gain", f"{potential_gain:.1f} t/h")
                with col3:
                    st.write("**Optimization Opportunities:**")
                    if bottleneck['stage'] == 'grinding':
                        st.write("- ⚙️ Increase mill capacity")
                        st.write("- 🔧 Optimize grinding parameters")
                        st.write("- 📈 Add parallel grinding circuit")
                    elif bottleneck['stage'] == 'flotation':
                        st.write("- 🧪 Optimize reagent dosing")
                        st.write("- ⏱️ Increase flotation residence time")
                        st.write("- 🔄 Add flotation cells")
                    else:
                        st.write("- 🔧 Equipment capacity upgrade")
                        st.write("- ⚙️ Process parameter optimization")
                        st.write("- 📊 Operational efficiency improvement")

# Capacity Utilization Analysis
if 'oxide' in plant.stage_results or 'sulphide' in plant.stage_results:
    st.subheader("📊 Equipment Capacity Utilization")
    
    capacity_data = []
    
    if 'oxide' in plant.stage_results:
        oxide_stages = plant.stage_results['oxide']
        
        # Calculate capacity utilization for each oxide stage
        for stage_name, stage_data in oxide_stages.items():
            if 'capacity' in stage_data and stage_name != 'feed':
                utilization = (stage_data['mass'] / stage_data['capacity']) * 100
                capacity_data.append({
                    'Process': 'Oxide',
                    'Stage': stage_name.title(),
                    'Actual Throughput (t/h)': stage_data['mass'],
                    'Design Capacity (t/h)': stage_data['capacity'],
                    'Utilization (%)': utilization,
                    'Available Capacity (t/h)': stage_data['capacity'] - stage_data['mass'],
                    'Status': 'Overloaded' if utilization > 100 else 'Critical' if utilization > 90 else 'Normal'
                })
    
    if 'sulphide' in plant.stage_results:
        sulphide_stages = plant.stage_results['sulphide']
        
        # Calculate capacity utilization for each sulphide stage
        for stage_name, stage_data in sulphide_stages.items():
            if 'capacity' in stage_data and stage_name != 'feed':
                if stage_name in ['cu_flotation', 'ni_flotation']:
                    throughput = stage_data['concentrate_mass']
                else:
                    throughput = stage_data['mass']
                    
                utilization = (throughput / stage_data['capacity']) * 100
                capacity_data.append({
                    'Process': 'Sulphide',
                    'Stage': stage_name.replace('_', ' ').title(),
                    'Actual Throughput (t/h)': throughput,
                    'Design Capacity (t/h)': stage_data['capacity'],
                    'Utilization (%)': utilization,
                    'Available Capacity (t/h)': stage_data['capacity'] - throughput,
                    'Status': 'Overloaded' if utilization > 100 else 'Critical' if utilization > 90 else 'Normal'
                })
    
    if capacity_data:
        capacity_df = pd.DataFrame(capacity_data)
        
        # Color code the dataframe based on status
        def color_status(val):
            if val == 'Overloaded':
                return 'background-color: #ffebee; color: #c62828'
            elif val == 'Critical':
                return 'background-color: #fff3e0; color: #ef6c00'
            else:
                return 'background-color: #e8f5e8; color: #2e7d32'
        
        styled_df = capacity_df.style.applymap(color_status, subset=['Status'])
        st.dataframe(styled_df, use_container_width=True)
        
        # Capacity utilization chart
        fig_capacity = px.bar(capacity_df, x='Stage', y='Utilization (%)', 
                             color='Process', barmode='group',
                             title="Equipment Capacity Utilization by Stage")
        fig_capacity.add_hline(y=100, line_dash="dash", line_color="red", 
                              annotation_text="Maximum Capacity")
        fig_capacity.add_hline(y=90, line_dash="dash", line_color="orange", 
                              annotation_text="Critical Threshold (90%)")
        st.plotly_chart(fig_capacity, use_container_width=True)
        
        # Summary metrics
        st.write("**Capacity Utilization Summary:**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            avg_utilization = capacity_df['Utilization (%)'].mean()
            st.metric("Average Utilization", f"{avg_utilization:.1f}%")
        with col2:
            overloaded_count = len(capacity_df[capacity_df['Status'] == 'Overloaded'])
            st.metric("Overloaded Stages", f"{overloaded_count}")
        with col3:
            critical_count = len(capacity_df[capacity_df['Status'] == 'Critical'])
            st.metric("Critical Stages", f"{critical_count}")
        with col4:
            total_spare_capacity = capacity_df['Available Capacity (t/h)'].sum()
            st.metric("Total Spare Capacity", f"{total_spare_capacity:.1f} t/h")

else:
    # Success message when no issues detected
    st.success("✅ **Material Flow Validation: All Clear**")
    st.write("No material flow warnings or bottlenecks detected. All process stages have sufficient capacity to handle current throughput rates.")

# Multi-Scenario Analysis & Risk Assessment
st.subheader("🎯 Multi-Scenario Analysis & Risk Assessment")

# Analysis type selection
analysis_type = st.selectbox(
    "Select Analysis Type:",
    ["Monte Carlo Simulation", "Risk Analysis", "Sensitivity Analysis", "Process Optimization"]
)

if analysis_type == "Monte Carlo Simulation":
    st.write("**Monte Carlo Simulation Settings:**")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        num_iterations = st.number_input("Number of Iterations", 100, 10000, 1000, 100)
        confidence_level = st.slider("Confidence Level (%)", 90, 99, 95, 1)
    with col2:
        # Parameter variation ranges
        st.write("**Parameter Variation Ranges (±%)**")
        feed_rate_var = st.slider("Feed Rate Variation", 5, 25, 10, 1, key="mc_feed_var")
        efficiency_var = st.slider("Efficiency Variation", 2, 15, 5, 1, key="mc_eff_var")
    with col3:
        grade_var = st.slider("Grade Variation", 5, 20, 10, 1, key="mc_grade_var")
        recovery_var = st.slider("Recovery Variation", 3, 15, 7, 1, key="mc_rec_var")
    
    if st.button("Run Monte Carlo Simulation", type="primary"):
        # Simulate Monte Carlo analysis
        np.random.seed(42)  # For reproducible results
        results_data = []
        
        for i in range(num_iterations):
            # Apply random variations to parameters
            varied_params = process_params.copy()
            varied_feed = feed_composition.copy()
            
            # Vary feed rates
            if feed_type in ["Oxide Feed", "Both Feeds"]:
                varied_params['oxide_feed_rate'] = oxide_feed_rate * (1 + np.random.normal(0, feed_rate_var/100))
            if feed_type in ["Sulphide Feed", "Both Feeds"]:
                varied_params['sulphide_feed_rate'] = sulphide_feed_rate * (1 + np.random.normal(0, feed_rate_var/100))
            
            # Vary efficiencies
            varied_params['sizing_efficiency'] = max(80, min(99, sizing_efficiency * (1 + np.random.normal(0, efficiency_var/100))))
            varied_params['oxide_grinding_efficiency'] = max(80, min(99, oxide_grinding_efficiency * (1 + np.random.normal(0, efficiency_var/100))))
            varied_params['sulphide_grinding_efficiency'] = max(80, min(99, sulphide_grinding_efficiency * (1 + np.random.normal(0, efficiency_var/100))))
            
            # Vary feed grades
            for metal in ['Cu', 'Pd', 'Pt', 'Au', 'Ni', 'Co']:
                if varied_feed[metal] > 0:
                    varied_feed[metal] = max(0.001, varied_feed[metal] * (1 + np.random.normal(0, grade_var/100)))
            
            # Vary recoveries
            varied_params['oxide_pd_recovery'] = max(60, min(90, oxide_pd_recovery * (1 + np.random.normal(0, recovery_var/100))))
            varied_params['final_cu_recovery'] = max(70, min(98, final_cu_recovery * (1 + np.random.normal(0, recovery_var/100))))
            varied_params['final_pd_recovery'] = max(60, min(98, final_pd_recovery * (1 + np.random.normal(0, recovery_var/100))))
            
            # Run simulation with varied parameters
            mc_plant = MetallurgicalPlant(varied_feed, varied_params)
            mc_plant.run_simulation()
            
            # Calculate total value
            total_value = 0
            if 'oxide' in mc_plant.results:
                total_value += (mc_plant.results['oxide']['pd_recovered'] * metal_prices['Pd'] + 
                               mc_plant.results['oxide']['au_recovered'] * metal_prices['Au'])
            if 'sulphide' in mc_plant.results:
                total_value += (mc_plant.results['sulphide']['cu_recovered'] * metal_prices['Cu'] +
                               mc_plant.results['sulphide']['pd_recovered'] * metal_prices['Pd'] +
                               mc_plant.results['sulphide']['pt_recovered'] * metal_prices['Pt'] +
                               mc_plant.results['sulphide']['au_recovered'] * metal_prices['Au'] +
                               mc_plant.results['sulphide']['ni_recovered'] * metal_prices['Ni'] +
                               mc_plant.results['sulphide']['co_recovered'] * metal_prices['Co'])
            
            results_data.append({
                'iteration': i + 1,
                'total_value': total_value,
                'cu_recovered': mc_plant.results.get('sulphide', {}).get('cu_recovered', 0),
                'pd_recovered': (mc_plant.results.get('oxide', {}).get('pd_recovered', 0) + 
                               mc_plant.results.get('sulphide', {}).get('pd_recovered', 0)),
                'au_recovered': (mc_plant.results.get('oxide', {}).get('au_recovered', 0) + 
                               mc_plant.results.get('sulphide', {}).get('au_recovered', 0))
            })
        
        mc_df = pd.DataFrame(results_data)
        
        # Statistical analysis
        st.write("**Monte Carlo Results:**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Mean Revenue", f"${mc_df['total_value'].mean():,.0f}/hour")
            st.metric(f"{confidence_level}% Confidence Lower", f"${mc_df['total_value'].quantile((100-confidence_level)/200):,.0f}/hour")
        with col2:
            st.metric("Median Revenue", f"${mc_df['total_value'].median():,.0f}/hour")
            st.metric(f"{confidence_level}% Confidence Upper", f"${mc_df['total_value'].quantile(1-(100-confidence_level)/200):,.0f}/hour")
        with col3:
            st.metric("Std Deviation", f"${mc_df['total_value'].std():,.0f}/hour")
            st.metric("Min Revenue", f"${mc_df['total_value'].min():,.0f}/hour")
        with col4:
            st.metric("Max Revenue", f"${mc_df['total_value'].max():,.0f}/hour")
            st.metric("Risk (CV)", f"{(mc_df['total_value'].std()/mc_df['total_value'].mean()*100):.1f}%")
        
        # Visualization
        fig_hist = px.histogram(mc_df, x='total_value', nbins=50, 
                               title="Revenue Distribution from Monte Carlo Simulation")
        fig_hist.add_vline(x=mc_df['total_value'].mean(), line_dash="dash", 
                          annotation_text=f"Mean: ${mc_df['total_value'].mean():,.0f}")
        st.plotly_chart(fig_hist, use_container_width=True)

elif analysis_type == "Risk Analysis":
    st.write("**Equipment Failure & Supply Disruption Analysis:**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Equipment Failure Scenarios:**")
        crusher_failure_prob = st.slider("Crusher Failure Probability (%)", 0, 20, 5, 1)
        mill_failure_prob = st.slider("Mill Failure Probability (%)", 0, 15, 3, 1)
        flotation_failure_prob = st.slider("Flotation Failure Probability (%)", 0, 10, 2, 1)
        
        # Equipment downtime impact
        equipment_downtime = st.slider("Equipment Downtime (hours)", 1, 48, 8, 1)
        
    with col2:
        st.write("**Supply Disruption Scenarios:**")
        supply_disruption_prob = st.slider("Supply Disruption Probability (%)", 0, 30, 10, 1)
        grade_reduction = st.slider("Feed Grade Reduction (%)", 0, 50, 20, 1)
        supply_shortage = st.slider("Feed Supply Shortage (%)", 0, 80, 30, 1)
    
    if st.button("Run Risk Analysis", type="primary"):
        risk_scenarios = []
        
        # Base case
        base_value = total_value_per_hour
        risk_scenarios.append({"Scenario": "Base Case", "Impact": 0, "Revenue": base_value, "Probability": "N/A"})
        
        # Equipment failure scenarios
        if feed_type in ["Sulphide Feed", "Both Feeds"]:
            crusher_impact = base_value * (crusher_failure_prob/100) * (equipment_downtime/24)
            risk_scenarios.append({
                "Scenario": "Crusher Failure", 
                "Impact": -crusher_impact, 
                "Revenue": base_value - crusher_impact,
                "Probability": f"{crusher_failure_prob}%"
            })
            
            mill_impact = base_value * (mill_failure_prob/100) * (equipment_downtime/24)
            risk_scenarios.append({
                "Scenario": "Mill Failure", 
                "Impact": -mill_impact, 
                "Revenue": base_value - mill_impact,
                "Probability": f"{mill_failure_prob}%"
            })
            
            flotation_impact = base_value * (flotation_failure_prob/100) * (equipment_downtime/24) * 0.8
            risk_scenarios.append({
                "Scenario": "Flotation Failure", 
                "Impact": -flotation_impact, 
                "Revenue": base_value - flotation_impact,
                "Probability": f"{flotation_failure_prob}%"
            })
        
        # Supply disruption scenarios
        grade_impact = base_value * (supply_disruption_prob/100) * (grade_reduction/100)
        risk_scenarios.append({
            "Scenario": "Grade Reduction", 
            "Impact": -grade_impact, 
            "Revenue": base_value - grade_impact,
            "Probability": f"{supply_disruption_prob}%"
        })
        
        supply_impact = base_value * (supply_disruption_prob/100) * (supply_shortage/100)
        risk_scenarios.append({
            "Scenario": "Supply Shortage", 
            "Impact": -supply_impact, 
            "Revenue": base_value - supply_impact,
            "Probability": f"{supply_disruption_prob}%"
        })
        
        risk_df = pd.DataFrame(risk_scenarios)
        st.dataframe(risk_df, use_container_width=True)
        
        # Risk visualization
        fig_risk = px.bar(risk_df[1:], x='Scenario', y='Impact', 
                         title="Risk Impact Analysis", color='Impact',
                         color_continuous_scale='Reds')
        st.plotly_chart(fig_risk, use_container_width=True)

elif analysis_type == "Sensitivity Analysis":
    st.write("**Sensitivity Analysis: Impact of Parameter Changes on Revenue**")
    
    # Parameter selection for sensitivity analysis
    selected_params = st.multiselect(
        "Select Parameters to Analyze:",
        ["Feed Rate", "Feed Grades", "Recovery Rates", "Process Efficiencies", "Metal Prices"],
        default=["Feed Grades", "Recovery Rates"]
    )
    
    variation_range = st.slider("Parameter Variation Range (±%)", 5, 50, 20, 5)
    
    if st.button("Run Sensitivity Analysis", type="primary"):
        sensitivity_results = []
        base_revenue = total_value_per_hour
        
        # Test each parameter
        for param_type in selected_params:
            if param_type == "Feed Rate":
                # Test feed rate variations
                for variation in [-variation_range, -variation_range/2, 0, variation_range/2, variation_range]:
                    test_params = process_params.copy()
                    if feed_type in ["Oxide Feed", "Both Feeds"]:
                        test_params['oxide_feed_rate'] = oxide_feed_rate * (1 + variation/100)
                    if feed_type in ["Sulphide Feed", "Both Feeds"]:
                        test_params['sulphide_feed_rate'] = sulphide_feed_rate * (1 + variation/100)
                    
                    test_plant = MetallurgicalPlant(feed_composition, test_params)
                    test_plant.run_simulation()
                    
                    test_value = 0
                    if 'oxide' in test_plant.results:
                        test_value += (test_plant.results['oxide']['pd_recovered'] * metal_prices['Pd'] + 
                                      test_plant.results['oxide']['au_recovered'] * metal_prices['Au'])
                    if 'sulphide' in test_plant.results:
                        test_value += (test_plant.results['sulphide']['cu_recovered'] * metal_prices['Cu'] +
                                      test_plant.results['sulphide']['pd_recovered'] * metal_prices['Pd'] +
                                      test_plant.results['sulphide']['pt_recovered'] * metal_prices['Pt'] +
                                      test_plant.results['sulphide']['au_recovered'] * metal_prices['Au'] +
                                      test_plant.results['sulphide']['ni_recovered'] * metal_prices['Ni'] +
                                      test_plant.results['sulphide']['co_recovered'] * metal_prices['Co'])
                    
                    sensitivity_results.append({
                        'Parameter': 'Feed Rate',
                        'Variation (%)': variation,
                        'Revenue': test_value,
                        'Change from Base': test_value - base_revenue,
                        'Sensitivity': (test_value - base_revenue) / base_revenue * 100 if variation != 0 else 0
                    })
            
            elif param_type == "Metal Prices":
                # Test metal price variations (using copper as example)
                for variation in [-variation_range, -variation_range/2, 0, variation_range/2, variation_range]:
                    test_prices = metal_prices.copy()
                    test_prices['Cu'] = metal_prices['Cu'] * (1 + variation/100)
                    test_prices['Pd'] = metal_prices['Pd'] * (1 + variation/100)
                    test_prices['Au'] = metal_prices['Au'] * (1 + variation/100)
                    
                    test_value = 0
                    if 'oxide' in plant.results:
                        test_value += (plant.results['oxide']['pd_recovered'] * test_prices['Pd'] + 
                                      plant.results['oxide']['au_recovered'] * test_prices['Au'])
                    if 'sulphide' in plant.results:
                        test_value += (plant.results['sulphide']['cu_recovered'] * test_prices['Cu'] +
                                      plant.results['sulphide']['pd_recovered'] * test_prices['Pd'] +
                                      plant.results['sulphide']['pt_recovered'] * test_prices['Pt'] +
                                      plant.results['sulphide']['au_recovered'] * test_prices['Au'] +
                                      plant.results['sulphide']['ni_recovered'] * test_prices['Ni'] +
                                      plant.results['sulphide']['co_recovered'] * test_prices['Co'])
                    
                    sensitivity_results.append({
                        'Parameter': 'Metal Prices',
                        'Variation (%)': variation,
                        'Revenue': test_value,
                        'Change from Base': test_value - base_revenue,
                        'Sensitivity': (test_value - base_revenue) / base_revenue * 100 if variation != 0 else 0
                    })
        
        if sensitivity_results:
            sens_df = pd.DataFrame(sensitivity_results)
            
            # Create sensitivity chart
            fig_sens = px.line(sens_df, x='Variation (%)', y='Revenue', color='Parameter',
                              title="Sensitivity Analysis: Revenue vs Parameter Variations")
            st.plotly_chart(fig_sens, use_container_width=True)
            
            # Sensitivity coefficients
            st.write("**Sensitivity Coefficients (Revenue change per 1% parameter change):**")
            for param in selected_params:
                param_data = sens_df[sens_df['Parameter'] == param]
                if len(param_data) > 2:
                    # Calculate average sensitivity
                    non_zero = param_data[param_data['Variation (%)'] != 0]
                    if len(non_zero) > 0:
                        avg_sensitivity = (non_zero['Sensitivity'] / non_zero['Variation (%)']).abs().mean()
                        st.metric(f"{param} Sensitivity", f"{avg_sensitivity:.2f}%")

elif analysis_type == "Process Optimization":
    st.write("**Automated Process Optimization**")
    
    # Optimization objective
    optimization_objective = st.selectbox(
        "Optimization Objective:",
        ["Maximize Revenue", "Maximize Metal Recovery", "Minimize Cost per Unit", "Maximize Profit Margin"]
    )
    
    # Constraints
    st.write("**Optimization Constraints:**")
    col1, col2 = st.columns(2)
    with col1:
        max_feed_rate = st.number_input("Maximum Feed Rate (t/h)", 
                                       int(max(oxide_feed_rate, sulphide_feed_rate)), 
                                       int(max(oxide_feed_rate, sulphide_feed_rate) * 1.5), 
                                       int(max(oxide_feed_rate, sulphide_feed_rate) * 1.2))
        min_recovery = st.slider("Minimum Overall Recovery (%)", 70, 95, 80, 1)
    with col2:
        max_operating_cost = st.number_input("Maximum Operating Cost ($/hour)", 10000, 100000, 50000, 5000)
        min_grade_threshold = st.slider("Minimum Feed Grade Threshold", 0.1, 2.0, 0.5, 0.1)
    
    if st.button("Run Process Optimization", type="primary"):
        # Simplified optimization algorithm (in practice, would use more sophisticated methods)
        best_config = None
        best_objective_value = float('-inf') if 'Maximize' in optimization_objective else float('inf')
        
        optimization_results = []
        
        # Test different configurations
        feed_rate_range = np.linspace(max(oxide_feed_rate, sulphide_feed_rate) * 0.8, max_feed_rate, 10)
        recovery_range = np.linspace(min_recovery, 95, 8)
        
        for test_feed_rate in feed_rate_range:
            for test_recovery in recovery_range:
                # Create test configuration
                test_params = process_params.copy()
                if feed_type in ["Oxide Feed", "Both Feeds"]:
                    test_params['oxide_feed_rate'] = min(test_feed_rate, max_feed_rate)
                    test_params['oxide_pd_recovery'] = test_recovery
                if feed_type in ["Sulphide Feed", "Both Feeds"]:
                    test_params['sulphide_feed_rate'] = min(test_feed_rate, max_feed_rate)
                    test_params['final_cu_recovery'] = test_recovery
                    test_params['final_pd_recovery'] = test_recovery
                
                # Run simulation
                test_plant = MetallurgicalPlant(feed_composition, test_params)
                test_plant.run_simulation()
                
                # Calculate objective value
                test_revenue = 0
                total_recovery = 0
                
                if 'oxide' in test_plant.results:
                    test_revenue += (test_plant.results['oxide']['pd_recovered'] * metal_prices['Pd'] + 
                                    test_plant.results['oxide']['au_recovered'] * metal_prices['Au'])
                    if plant.stage_results.get('oxide', {}).get('feed', {}).get('pd', 0) > 0:
                        total_recovery += test_plant.results['oxide']['pd_recovered'] / plant.stage_results['oxide']['feed']['pd'] * 100
                
                if 'sulphide' in test_plant.results:
                    test_revenue += (test_plant.results['sulphide']['cu_recovered'] * metal_prices['Cu'] +
                                    test_plant.results['sulphide']['pd_recovered'] * metal_prices['Pd'] +
                                    test_plant.results['sulphide']['pt_recovered'] * metal_prices['Pt'] +
                                    test_plant.results['sulphide']['au_recovered'] * metal_prices['Au'] +
                                    test_plant.results['sulphide']['ni_recovered'] * metal_prices['Ni'] +
                                    test_plant.results['sulphide']['co_recovered'] * metal_prices['Co'])
                
                # Estimated operating cost (simplified)
                operating_cost = test_feed_rate * 15  # $15/tonne processing cost
                
                if optimization_objective == "Maximize Revenue":
                    objective_value = test_revenue
                elif optimization_objective == "Maximize Metal Recovery":
                    objective_value = total_recovery
                elif optimization_objective == "Minimize Cost per Unit":
                    objective_value = -operating_cost / max(1, test_revenue) * 1000
                else:  # Maximize Profit Margin
                    objective_value = (test_revenue - operating_cost) / max(1, test_revenue) * 100
                
                optimization_results.append({
                    'Feed Rate': test_feed_rate,
                    'Recovery': test_recovery,
                    'Revenue': test_revenue,
                    'Operating Cost': operating_cost,
                    'Objective Value': objective_value
                })
                
                # Check if this is the best configuration
                is_better = (optimization_objective.startswith('Maximize') and objective_value > best_objective_value) or \
                           (optimization_objective.startswith('Minimize') and objective_value < best_objective_value)
                
                if is_better and operating_cost <= max_operating_cost and total_recovery >= min_recovery:
                    best_objective_value = objective_value
                    best_config = {
                        'feed_rate': test_feed_rate,
                        'recovery': test_recovery,
                        'revenue': test_revenue,
                        'cost': operating_cost,
                        'objective': objective_value
                    }
        
        if best_config:
            st.success("**Optimization Complete!**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Optimal Feed Rate", f"{best_config['feed_rate']:.0f} t/h")
                st.metric("Optimal Recovery", f"{best_config['recovery']:.1f}%")
            with col2:
                st.metric("Projected Revenue", f"${best_config['revenue']:,.0f}/hour")
                st.metric("Operating Cost", f"${best_config['cost']:,.0f}/hour")
            with col3:
                st.metric("Objective Value", f"{best_config['objective']:.2f}")
                st.metric("Profit Margin", f"{((best_config['revenue']-best_config['cost'])/best_config['revenue']*100):.1f}%")
            
            # Optimization surface plot
            opt_df = pd.DataFrame(optimization_results)
            fig_opt = px.scatter_3d(opt_df, x='Feed Rate', y='Recovery', z='Objective Value',
                                   color='Revenue', title="Optimization Surface")
            st.plotly_chart(fig_opt, use_container_width=True)
        else:
            st.error("No feasible solution found within the given constraints.")

# Metal value breakdown
if feed_type in ["Oxide Feed", "Sulphide Feed", "Both Feeds"]:
    st.subheader("📊 Revenue Breakdown by Metal")
    
    # Create revenue breakdown chart
    metals_produced = []
    revenue_values = []
    
    if 'oxide' in plant.results:
        if plant.results['oxide']['pd_recovered'] > 0:
            metals_produced.append('Pd (Oxide)')
            revenue_values.append(plant.results['oxide']['pd_recovered'] * metal_prices['Pd'])
        if plant.results['oxide']['au_recovered'] > 0:
            metals_produced.append('Au (Oxide)')
            revenue_values.append(plant.results['oxide']['au_recovered'] * metal_prices['Au'])
    
    if 'sulphide' in plant.results:
        if plant.results['sulphide']['cu_recovered'] > 0:
            metals_produced.append('Cu (Sulphide)')
            revenue_values.append(plant.results['sulphide']['cu_recovered'] * metal_prices['Cu'])
        if plant.results['sulphide']['pd_recovered'] > 0:
            metals_produced.append('Pd (Sulphide)')
            revenue_values.append(plant.results['sulphide']['pd_recovered'] * metal_prices['Pd'])
        if plant.results['sulphide']['pt_recovered'] > 0:
            metals_produced.append('Pt (Sulphide)')
            revenue_values.append(plant.results['sulphide']['pt_recovered'] * metal_prices['Pt'])
        if plant.results['sulphide']['au_recovered'] > 0:
            metals_produced.append('Au (Sulphide)')
            revenue_values.append(plant.results['sulphide']['au_recovered'] * metal_prices['Au'])
        if plant.results['sulphide']['ni_recovered'] > 0:
            metals_produced.append('Ni (Sulphide)')
            revenue_values.append(plant.results['sulphide']['ni_recovered'] * metal_prices['Ni'])
        if plant.results['sulphide']['co_recovered'] > 0:
            metals_produced.append('Co (Sulphide)')
            revenue_values.append(plant.results['sulphide']['co_recovered'] * metal_prices['Co'])
    
    if metals_produced:
        fig_revenue = px.pie(
            values=revenue_values,
            names=metals_produced,
            title="Revenue Contribution by Metal ($/hour)"
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
        
        # Revenue breakdown table
        revenue_df = pd.DataFrame({
            'Metal': metals_produced,
            'Revenue ($/hour)': [f"${val:,.0f}" for val in revenue_values],
            'Revenue ($/day)': [f"${val*24:,.0f}" for val in revenue_values],
            'Revenue ($/year)': [f"${val*24*365:,.0f}" for val in revenue_values]
        })
        st.dataframe(revenue_df, use_container_width=True)
st.markdown("---")
st.markdown("**Note:** This simulator uses simplified metallurgical models for demonstration purposes. Actual plant performance may vary based on ore characteristics, equipment efficiency, and operating conditions.")
