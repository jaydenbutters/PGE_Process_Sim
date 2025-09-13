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
        # Calculate total value per hour for base case
        total_value_per_hour = 0
        if 'oxide' in plant.results:
            total_value_per_hour += (plant.results['oxide']['pd_recovered'] * metal_prices['Pd'] + 
                                   plant.results['oxide']['au_recovered'] * metal_prices['Au'])
        if 'sulphide' in plant.results:
            total_value_per_hour += (plant.results['sulphide']['cu_recovered'] * metal_prices['Cu'] +
                                   plant.results['sulphide']['pd_recovered'] * metal_prices['Pd'] +
                                   plant.results['sulphide']['pt_recovered'] * metal_prices['Pt'] +
                                   plant.results['sulphide']['au_recovered'] * metal_prices['Au'] +
                                   plant.results['sulphide']['ni_recovered'] * metal_prices['Ni'] +
                                   plant.results['sulphide']['co_recovered'] * metal_prices['Co'])
        
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
        
        # Calculate base revenue
        base_revenue = 0
        if 'oxide' in plant.results:
            base_revenue += (plant.results['oxide']['pd_recovered'] * metal_prices['Pd'] + 
                           plant.results['oxide']['au_recovered'] * metal_prices['Au'])
        if 'sulphide' in plant.results:
            base_revenue += (plant.results['sulphide']['cu_recovered'] * metal_prices['Cu'] +
                           plant.results['sulphide']['pd_recovered'] * metal_prices['Pd'] +
                           plant.results['sulphide']['pt_recovered'] * metal_prices['Pt'] +
                           plant.results['sulphide']['au_recovered'] * metal_prices['Au'] +
                           plant.results['sulphide']['ni_recovered'] * metal_prices['Ni'] +
                           plant.results['sulphide']['co_recovered'] * metal_prices['Co'])
        
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
                        'cost': operating_cost,        total_concentrate = cu_concentrate_mass + ni_concentrate_mass
        if not self.validate_material_flow("Pressure Oxidation", total_concentrate, pressure_ox_capacity, "sulphide"):
            pressure_ox_efficiency = pressure_ox_efficiency * 0.95  # Reduced efficiency when overloaded
        
        # Apply pressure oxidation to concentrates
        cu_after_pressure_ox = cu_in_concentrate * pressure_ox_efficiency
        pd_cu_after_pressure_ox = pd_in_cu_concentrate * pressure_ox_efficiency
        pt_cu_after_pressure_ox = pt_in_cu_concentrate * pressure_ox_efficiency
        au_cu_after_pressure_ox = au_in_cu_concentrate * pressure_ox_efficiency
        
        ni_after_pressure_ox = ni_in_concentrate * pressure_ox_efficiency
        co_after_pressure_ox = co_in_concentrate * pressure_ox_efficiency
        pd_ni_after_pressure_ox = pd_in_ni_concentrate * pressure_ox_efficiency
        pt_ni_after_pressure_ox = pt_in_ni_concentrate * pressure_ox_efficiency
        au_ni_after_pressure_ox = au_in_ni_concentrate * pressure_ox_efficiency
        
        # Stage 7: Final Metal Recovery
        final_cu_recovery = self.process_params['final_cu_recovery'] / 100
        final_pd_recovery = self.process_params['final_pd_recovery'] / 100
        final_pt_recovery = self.process_params['final_pt_recovery'] / 100
        final_au_recovery = self.process_params['final_au_recovery'] / 100
        final_ni_recovery = self.process_params['final_ni_recovery'] / 100
        final_co_recovery = self.process_params['final_co_recovery'] / 100
        
        # Final metal production
        cu_final = cu_after_pressure_ox * final_cu_recovery
        pd_final = (pd_cu_after_pressure_ox + pd_ni_after_pressure_ox) * final_pd_recovery
        pt_final = (pt_cu_after_pressure_ox + pt_ni_after_pressure_ox) * final_pt_recovery
        au_final = (au_cu_after_pressure_ox + au_ni_after_pressure_ox) * final_au_recovery
        ni_final = ni_after_pressure_ox * final_ni_recovery
        co_final = co_after_pressure_ox * final_co_recovery
        
        # Store detailed stage results with capacity information
        self.stage_results['sulphide'] = {
            'feed': {'mass': feed_mass, 'cu': feed_cu, 'pd': feed_pd, 'pt': feed_pt, 'au': feed_au, 'ni': feed_ni, 'co': feed_co},
            'crushing': {'mass': crushed_mass, 'cu': crushed_cu, 'pd': crushed_pd, 'pt': crushed_pt, 'au': crushed_au, 'ni': crushed_ni, 'co': crushed_co, 'losses': crushing_losses, 'capacity': crushing_capacity},
            'grinding': {'mass': ground_mass, 'cu': ground_cu, 'pd': ground_pd, 'pt': ground_pt, 'au': ground_au, 'ni': ground_ni, 'co': ground_co, 'losses': grinding_losses, 'capacity': grinding_capacity},
            'cu_flotation': {'concentrate_mass': cu_concentrate_mass, 'cu': cu_in_concentrate, 'pd': pd_in_cu_concentrate, 'pt': pt_in_cu_concentrate, 'au': au_in_cu_concentrate, 'capacity': cu_flotation_capacity},
            'ni_flotation': {'concentrate_mass': ni_concentrate_mass, 'ni': ni_in_concentrate, 'co': co_in_concentrate, 'pd': pd_in_ni_concentrate, 'pt': pt_in_ni_concentrate, 'au': au_in_ni_concentrate, 'capacity': ni_flotation_capacity},
            'pressure_oxidation': {'cu': cu_after_pressure_ox, 'ni': ni_after_pressure_ox, 'co': co_after_pressure_ox, 'capacity': pressure_ox_capacity},
            'final_products': {'cu': cu_final, 'pd': pd_final, 'pt': pt_final, 'au': au_final, 'ni': ni_final, 'co': co_final},
            'tailings': {'mass': flotation_tailings}
        }
        
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
            'tailings_mass': flotation_tailings
        }
        
    def run_simulation(self):
        """Run the complete simulation with material flow validation"""
        # Clear previous warnings and bottlenecks
        self.material_flow_warnings = []
        self.bottlenecks = []
        
        if feed_type in ["Oxide Feed", "Both Feeds"]:
            self.process_oxide_feed()
        if feed_type in ["Sulphide Feed", "Both Feeds"]:
            self.process_sulphide_feed()
            
        # Check for process bottlenecks after simulation
        self.check_process_bottlenecks()

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
    'oxide_feed_rate': oxide_feed_rate,
    'sulphide_feed_rate': sulphide_feed_rate,
    'sizing_efficiency': sizing_efficiency,
    'oxide_grinding_efficiency': oxide_grinding_efficiency,
    'sulphide_grinding_efficiency': sulphide_grinding_efficiency,
    'leaching_efficiency': leaching_efficiency,
    'crushing_efficiency': crushing_efficiency,
    'cu_flotation_efficiency': cu_flotation_efficiency,
    'cu_flotation_recovery': cu_flotation_recovery,
    'ni_flotation_efficiency': ni_flotation_efficiency,
    'ni_flotation_recovery': ni_flotation_recovery,
    'co_flotation_recovery': co_flotation_recovery,
    'pgm_to_cu_concentrate': pgm_to_cu_concentrate,
    'pgm_to_ni_concentrate': pgm_to_ni_concentrate,
    'pressure_oxidation_efficiency': pressure_oxidation_efficiency,
    'oxide_pd_recovery': oxide_pd_recovery,
    'oxide_au_recovery': oxide_au_recovery,
    'final_cu_recovery': final_cu_recovery,
    'final_pd_recovery': final_pd_recovery,
    'final_pt_recovery': final_pt_recovery,
    'final_au_recovery': final_au_recovery,
    'final_ni_recovery': final_ni_recovery,
    'final_co_recovery': final_co_recovery
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
        
        st.dataframe(massimport streamlit as st
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
st.sidebar.header("Production Scenario Selection")

# Production scenario selection
production_scenario = st.sidebar.selectbox(
    "Select Production Scenario:",
    ["15Mtpa Case", "30Mtpa Case", "Custom"]
)

# Define baseline scenarios
scenarios = {
    "15Mtpa Case": {
        "total_mined": 680,  # Mt
        "total_processed": 240,  # Mt
        "3E_grade": 0.95,  # g/t (Pd+Pt+Au)
        "ni_grade": 0.16,  # %
        "cu_grade": 0.11,  # %
        "co_grade": 0.017,  # %
        "pd_recovery": 78,  # %
        "pt_recovery": 45,  # %
        "au_recovery": 66,  # %
        "ni_recovery": 43,  # %
        "cu_recovery": 80,  # %
        "co_recovery": 42,  # %
        "oxide_throughput": 2,  # Mtpa
        "sulphide_throughput": 12.5,  # Mtpa (mid-range of 7.5-15)
        "mine_life_sulphide": 19,  # years
        "mine_life_oxide": 4  # years
    },
    "30Mtpa Case": {
        "total_mined": 1300,  # Mt
        "total_processed": 440,  # Mt
        "3E_grade": 0.85,  # g/t (Pd+Pt+Au)
        "ni_grade": 0.16,  # %
        "cu_grade": 0.09,  # %
        "co_grade": 0.016,  # %
        "pd_recovery": 77,  # %
        "pt_recovery": 43,  # %
        "au_recovery": 66,  # %
        "ni_recovery": 41,  # %
        "cu_recovery": 76,  # %
        "co_recovery": 40,  # %
        "oxide_throughput": 2,  # Mtpa
        "sulphide_throughput": 22.5,  # Mtpa (mid-range of 15-30)
        "mine_life_sulphide": 18,  # years
        "mine_life_oxide": 4  # years
    }
}

# Feed selection
feed_type = st.sidebar.selectbox("Select Feed Type:", ["Oxide Feed", "Sulphide Feed", "Both Feeds"])

if production_scenario == "Custom":
    # Custom input parameters
    st.sidebar.subheader("Feed Composition")
    
    # Calculate individual metal grades from 3E grade
    total_3e_grade = st.sidebar.slider("3E Grade (Pd+Pt+Au) g/t", 0.1, 2.0, 0.95, 0.05)
    
    # Approximate split of 3E metals (based on typical ratios)
    pd_ratio = st.sidebar.slider("Pd ratio in 3E (%)", 30, 70, 50, 5) / 100
    pt_ratio = st.sidebar.slider("Pt ratio in 3E (%)", 20, 50, 30, 5) / 100
    au_ratio = 1 - pd_ratio - pt_ratio
    
    pd_grade = total_3e_grade * pd_ratio / 1000  # Convert g/t to %
    pt_grade = total_3e_grade * pt_ratio / 1000
    au_grade = total_3e_grade * au_ratio / 1000
    
    cu_grade = st.sidebar.slider("Copper (%)", 0.05, 0.5, 0.11, 0.01)
    ni_grade = st.sidebar.slider("Nickel (%)", 0.05, 0.5, 0.16, 0.01) if feed_type in ["Sulphide Feed", "Both Feeds"] else 0
    co_grade = st.sidebar.slider("Cobalt (%)", 0.005, 0.05, 0.017, 0.001) if feed_type in ["Sulphide Feed", "Both Feeds"] else 0
    
    # Process parameters
    st.sidebar.subheader("Process Parameters")
    oxide_throughput_mtpa = st.sidebar.slider("Oxide Throughput (Mtpa)", 0.5, 5.0, 2.0, 0.5)
    sulphide_throughput_mtpa = st.sidebar.slider("Sulphide Throughput (Mtpa)", 5.0, 35.0, 15.0, 2.5)
    
    # Convert to tonnes per hour
    oxide_throughput = oxide_throughput_mtpa * 1000000 / (365 * 24)
    sulphide_throughput = sulphide_throughput_mtpa * 1000000 / (365 * 24)
    
    # Recovery rates
    st.sidebar.subheader("Recovery Rates (%)")
    pd_recovery = st.sidebar.slider("Pd Recovery", 70, 85, 78, 1)
    pt_recovery = st.sidebar.slider("Pt Recovery", 35, 55, 45, 1)
    au_recovery = st.sidebar.slider("Au Recovery", 60, 75, 66, 1)
    ni_recovery = st.sidebar.slider("Ni Recovery", 35, 50, 43, 1)
    cu_recovery = st.sidebar.slider("Cu Recovery", 70, 85, 80, 1)
    co_recovery = st.sidebar.slider("Co Recovery", 35, 50, 42, 1)
    
else:
    # Use predefined scenario
    scenario_data = scenarios[production_scenario]
    
    st.sidebar.subheader(f"{production_scenario} Parameters")
    st.sidebar.write(f"**Total Material to be Mined:** {scenario_data['total_mined']} Mt")
    st.sidebar.write(f"**Total Material Processed:** {scenario_data['total_processed']} Mt")
    st.sidebar.write(f"**Mine Life (Sulphide):** {scenario_data['mine_life_sulphide']} years")
    st.sidebar.write(f"**Mine Life (Oxide):** {scenario_data['mine_life_oxide']} years")
    
    # Set grades based on scenario
    total_3e_grade = scenario_data['3E_grade']
    
    # Approximate 3E metal split (typical ratios)
    pd_grade = total_3e_grade * 0.5 / 1000  # 50% of 3E, convert g/t to %
    pt_grade = total_3e_grade * 0.3 / 1000  # 30% of 3E
    au_grade = total_3e_grade * 0.2 / 1000  # 20% of 3E
    
    cu_grade = scenario_data['cu_grade']
    ni_grade = scenario_data['ni_grade'] if feed_type in ["Sulphide Feed", "Both Feeds"] else 0
    co_grade = scenario_data['co_grade'] if feed_type in ["Sulphide Feed", "Both Feeds"] else 0
    
    # Set throughput (convert Mtpa to t/h)
    oxide_throughput = scenario_data['oxide_throughput'] * 1000000 / (365 * 24)
    sulphide_throughput = scenario_data['sulphide_throughput'] * 1000000 / (365 * 24)
    
    # Set recovery rates
    pd_recovery = scenario_data['pd_recovery']
    pt_recovery = scenario_data['pt_recovery']
    au_recovery = scenario_data['au_recovery']
    ni_recovery = scenario_data['ni_recovery']
    cu_recovery = scenario_data['cu_recovery']
    co_recovery = scenario_data['co_recovery']

# Additional process parameters
st.sidebar.subheader("Process Stage Parameters")

# Oxide Process Controls
if feed_type in ["Oxide Feed", "Both Feeds"]:
    st.sidebar.write("**Oxide Process Controls:**")
    oxide_feed_rate = st.sidebar.number_input("Oxide Feed Rate (t/h)", 100, 2000, int(oxide_throughput), 50, key="oxide_feed")
    sizing_efficiency = st.sidebar.slider("Sizing Efficiency (%)", 85, 99, 98, 1, key="sizing_eff")
    oxide_grinding_efficiency = st.sidebar.slider("Oxide Grinding Efficiency (%)", 85, 98, 92, 1, key="oxide_grind_eff")
    leaching_efficiency = st.sidebar.slider("Leaching Efficiency (%)", 80, 95, 88, 1, key="leach_eff")
    
    # Individual metal recoveries in leaching
    st.sidebar.write("*Leaching Metal Recoveries:*")
    oxide_pd_recovery = st.sidebar.slider("Oxide Pd Recovery (%)", 70, 85, pd_recovery, 1, key="oxide_pd_rec")
    oxide_au_recovery = st.sidebar.slider("Oxide Au Recovery (%)", 85, 95, 90, 1, key="oxide_au_rec")
else:
    oxide_feed_rate = 0
    sizing_efficiency = 98
    oxide_grinding_efficiency = 92
    leaching_efficiency = 88
    oxide_pd_recovery = 75
    oxide_au_recovery = 90

# Sulphide Process Controls
if feed_type in ["Sulphide Feed", "Both Feeds"]:
    st.sidebar.write("**Sulphide Process Controls:**")
    sulphide_feed_rate = st.sidebar.number_input("Sulphide Feed Rate (t/h)", 500, 5000, int(sulphide_throughput), 100, key="sulphide_feed")
    crushing_efficiency = st.sidebar.slider("Crushing Efficiency (%)", 90, 99, 98, 1, key="crush_eff")
    sulphide_grinding_efficiency = st.sidebar.slider("Sulphide Grinding Efficiency (%)", 85, 98, 92, 1, key="sulphide_grind_eff")
    
    # Flotation stage controls
    st.sidebar.write("*Flotation Stage Controls:*")
    cu_flotation_efficiency = st.sidebar.slider("Cu Flotation Efficiency (%)", 75, 95, 85, 1, key="cu_flot_eff")
    cu_flotation_recovery = st.sidebar.slider("Cu Flotation Recovery (%)", 70, 85, cu_recovery, 1, key="cu_flot_rec")
    
    ni_flotation_efficiency = st.sidebar.slider("Ni Flotation Efficiency (%)", 70, 90, 80, 1, key="ni_flot_eff")
    ni_flotation_recovery = st.sidebar.slider("Ni Flotation Recovery (%)", 35, 50, ni_recovery, 1, key="ni_flot_rec")
    co_flotation_recovery = st.sidebar.slider("Co Flotation Recovery (%)", 35, 50, co_recovery, 1, key="co_flot_rec")
    
    # PGM distribution in concentrates
    st.sidebar.write("*PGM Distribution:*")
    pgm_to_cu_concentrate = st.sidebar.slider("PGMs to Cu Concentrate (%)", 60, 85, 70, 5, key="pgm_cu_dist")
    pgm_to_ni_concentrate = st.sidebar.slider("PGMs to Ni Concentrate (%)", 10, 35, 25, 5, key="pgm_ni_dist")
    
    # Downstream processing
    st.sidebar.write("*Downstream Processing:*")
    pressure_oxidation_efficiency = st.sidebar.slider("Pressure Oxidation Efficiency (%)", 90, 98, 95, 1, key="press_ox_eff")
    
    # Final metal recoveries from concentrates
    st.sidebar.write("*Final Metal Recovery from Concentrates:*")
    final_cu_recovery = st.sidebar.slider("Final Cu Recovery (%)", 85, 98, 95, 1, key="final_cu_rec")
    final_pd_recovery = st.sidebar.slider("Final Pd Recovery (%)", 85, 98, pd_recovery, 1, key="final_pd_rec")
    final_pt_recovery = st.sidebar.slider("Final Pt Recovery (%)", 80, 95, pt_recovery, 1, key="final_pt_rec")
    final_au_recovery = st.sidebar.slider("Final Au Recovery (%)", 85, 98, au_recovery, 1, key="final_au_rec")
    final_ni_recovery = st.sidebar.slider("Final Ni Recovery (%)", 85, 98, 92, 1, key="final_ni_rec")
    final_co_recovery = st.sidebar.slider("Final Co Recovery (%)", 85, 98, 90, 1, key="final_co_rec")
else:
    sulphide_feed_rate = 0
    crushing_efficiency = 98
    sulphide_grinding_efficiency = 92
    cu_flotation_efficiency = 85
    cu_flotation_recovery = 80
    ni_flotation_efficiency = 80
    ni_flotation_recovery = 43
    co_flotation_recovery = 42
    pgm_to_cu_concentrate = 70
    pgm_to_ni_concentrate = 25
    pressure_oxidation_efficiency = 95
    final_cu_recovery = 95
    final_pd_recovery = 78
    final_pt_recovery = 45
    final_au_recovery = 66
    final_ni_recovery = 92
    final_co_recovery = 90

# Interactive metal prices
st.sidebar.subheader("Metal Prices (USD/kg)")
metal_prices = {
    'Cu': st.sidebar.number_input("Copper Price", 1.0, 20.0, 8.5, 0.1),
    'Pd': st.sidebar.number_input("Palladium Price", 10000, 80000, 32000, 1000),
    'Pt': st.sidebar.number_input("Platinum Price", 10000, 60000, 28000, 1000),
    'Au': st.sidebar.number_input("Gold Price", 30000, 100000, 65000, 1000),
    'Ni': st.sidebar.number_input("Nickel Price", 5.0, 50.0, 18.0, 1.0),
    'Co': st.sidebar.number_input("Cobalt Price", 10.0, 80.0, 35.0, 1.0)
}

class MetallurgicalPlant:
    def __init__(self, feed_composition, process_params):
        self.feed_composition = feed_composition
        self.process_params = process_params
        self.results = {}
        self.stage_results = {}
        self.material_flow_warnings = []
        self.bottlenecks = []
        
    def validate_material_flow(self, stage_name, required_mass, available_mass, process_type="oxide"):
        """Validate if upstream process can provide sufficient material for downstream process"""
        if required_mass > available_mass:
            shortage = required_mass - available_mass
            shortage_percent = (shortage / required_mass) * 100
            
            warning = {
                'process_type': process_type,
                'stage': stage_name,
                'required_mass': required_mass,
                'available_mass': available_mass,
                'shortage': shortage,
                'shortage_percent': shortage_percent,
                'severity': 'Critical' if shortage_percent > 50 else 'High' if shortage_percent > 25 else 'Moderate'
            }
            
            self.material_flow_warnings.append(warning)
            return False
        return True
        
    def check_process_bottlenecks(self):
        """Identify process bottlenecks based on material flow constraints"""
        self.bottlenecks = []
        
        # Check oxide process bottlenecks
        if 'oxide' in self.stage_results:
            oxide_stages = self.stage_results['oxide']
            
            # Check each stage capacity vs demand
            stages = ['sizing', 'grinding', 'leaching']
            stage_masses = [
                oxide_stages['sizing']['mass'],
                oxide_stages['grinding']['mass'],
                oxide_stages['leaching']['mass']
            ]
            
            # Find the limiting stage
            min_throughput_idx = stage_masses.index(min(stage_masses))
            min_throughput = stage_masses[min_throughput_idx]
            
            if min_throughput < oxide_stages['feed']['mass'] * 0.8:  # If significant loss
                self.bottlenecks.append({
                    'process': 'Oxide',
                    'stage': stages[min_throughput_idx],
                    'limiting_throughput': min_throughput,
                    'feed_rate': oxide_stages['feed']['mass'],
                    'efficiency_loss': (1 - min_throughput / oxide_stages['feed']['mass']) * 100
                })
        
        # Check sulphide process bottlenecks
        if 'sulphide' in self.stage_results:
            sulphide_stages = self.stage_results['sulphide']
            
            # Check crushing -> grinding -> flotation capacity
            crushing_output = sulphide_stages['crushing']['mass']
            grinding_output = sulphide_stages['grinding']['mass']
            flotation_capacity = sulphide_stages['cu_flotation']['concentrate_mass'] + sulphide_stages['ni_flotation']['concentrate_mass']
            
            if grinding_output < crushing_output * 0.9:
                self.bottlenecks.append({
                    'process': 'Sulphide',
                    'stage': 'grinding',
                    'limiting_throughput': grinding_output,
                    'upstream_capacity': crushing_output,
                    'efficiency_loss': (1 - grinding_output / crushing_output) * 100
                })
            
            if flotation_capacity < grinding_output * 0.3:  # Expected concentrate yield
                self.bottlenecks.append({
                    'process': 'Sulphide',
                    'stage': 'flotation',
                    'limiting_throughput': flotation_capacity,
                    'upstream_capacity': grinding_output,
                    'efficiency_loss': (1 - flotation_capacity / (grinding_output * 0.3)) * 100
                })
        
    def process_oxide_feed(self):
        """Process oxide feed through sizing, grinding, and leaching with material flow validation"""
        # Stage 1: Feed
        feed_mass = self.process_params['oxide_feed_rate']
        feed_pd = feed_mass * self.feed_composition['Pd'] / 100
        feed_au = feed_mass * self.feed_composition['Au'] / 100
        
        # Stage 2: Sizing
        sizing_efficiency = self.process_params['sizing_efficiency'] / 100
        sizing_capacity = feed_mass * 1.2  # Sizing equipment can handle 20% more than feed rate
        
        # Check if sizing can handle the feed rate
        if not self.validate_material_flow("Sizing", feed_mass, sizing_capacity, "oxide"):
            # Reduce throughput to equipment capacity
            effective_feed_mass = sizing_capacity
        else:
            effective_feed_mass = feed_mass
            
        sized_mass = effective_feed_mass * sizing_efficiency
        sized_pd = feed_pd * (effective_feed_mass / feed_mass) * sizing_efficiency
        sized_au = feed_au * (effective_feed_mass / feed_mass) * sizing_efficiency
        sizing_losses = effective_feed_mass - sized_mass
        
        # Stage 3: Grinding
        grinding_efficiency = self.process_params['oxide_grinding_efficiency'] / 100
        grinding_capacity = sized_mass * 1.1  # Grinding can handle 10% more than sized output
        
        # Check grinding capacity constraint
        if not self.validate_material_flow("Grinding", sized_mass, grinding_capacity, "oxide"):
            effective_sized_mass = grinding_capacity
            grinding_efficiency_adjusted = grinding_efficiency * 0.95  # Reduce efficiency when overloaded
        else:
            effective_sized_mass = sized_mass
            grinding_efficiency_adjusted = grinding_efficiency
            
        ground_mass = effective_sized_mass * grinding_efficiency_adjusted
        ground_pd = sized_pd * (effective_sized_mass / sized_mass) * grinding_efficiency_adjusted
        ground_au = sized_au * (effective_sized_mass / sized_mass) * grinding_efficiency_adjusted
        grinding_losses = effective_sized_mass - ground_mass
        
        # Stage 4: Leaching
        leaching_efficiency = self.process_params['leaching_efficiency'] / 100
        leaching_capacity = ground_mass * 1.05  # Leaching can handle 5% more than ground output
        
        # Check leaching capacity
        if not self.validate_material_flow("Leaching", ground_mass, leaching_capacity, "oxide"):
            effective_ground_mass = leaching_capacity
        else:
            effective_ground_mass = ground_mass
            
        leach_mass = effective_ground_mass * leaching_efficiency
        
        # Individual metal recoveries in leaching
        pd_recovery_rate = self.process_params['oxide_pd_recovery'] / 100
        au_recovery_rate = self.process_params['oxide_au_recovery'] / 100
        
        pd_recovered = ground_pd * (effective_ground_mass / ground_mass) * pd_recovery_rate
        au_recovered = ground_au * (effective_ground_mass / ground_mass) * au_recovery_rate
        
        # Stage 5: Tailings
        tailings_mass = effective_ground_mass - leach_mass
        tailings_pd = ground_pd * (effective_ground_mass / ground_mass) - pd_recovered
        tailings_au = ground_au * (effective_ground_mass / ground_mass) - au_recovered
        
        # Store stage-by-stage results
        self.stage_results['oxide'] = {
            'feed': {'mass': feed_mass, 'pd': feed_pd, 'au': feed_au},
            'sizing': {'mass': sized_mass, 'pd': sized_pd, 'au': sized_au, 'losses': sizing_losses, 'capacity': sizing_capacity},
            'grinding': {'mass': ground_mass, 'pd': ground_pd, 'au': ground_au, 'losses': grinding_losses, 'capacity': grinding_capacity},
            'leaching': {'mass': leach_mass, 'pd_recovered': pd_recovered, 'au_recovered': au_recovered, 'capacity': leaching_capacity},
            'tailings': {'mass': tailings_mass, 'pd': tailings_pd, 'au': tailings_au}
        }
        
        self.results['oxide'] = {
            'feed_mass': feed_mass,
            'sized_mass': sized_mass,
            'ground_mass': ground_mass,
            'pd_recovered': pd_recovered,
            'au_recovered': au_recovered,
            'tailings_mass': tailings_mass,
            'leach_solution_mass': leach_mass
        }
        
    def process_sulphide_feed(self):
        """Process sulphide feed through all stages with detailed material flow validation"""
        # Stage 1: Feed
        feed_mass = self.process_params['sulphide_feed_rate']
        feed_cu = feed_mass * self.feed_composition['Cu'] / 100
        feed_pd = feed_mass * self.feed_composition['Pd'] / 100
        feed_pt = feed_mass * self.feed_composition['Pt'] / 100
        feed_au = feed_mass * self.feed_composition['Au'] / 100
        feed_ni = feed_mass * self.feed_composition['Ni'] / 100
        feed_co = feed_mass * self.feed_composition['Co'] / 100
        
        # Stage 2: Crushing
        crushing_efficiency = self.process_params['crushing_efficiency'] / 100
        crushing_capacity = feed_mass * 1.3  # Crushers typically have higher capacity
        
        if not self.validate_material_flow("Crushing", feed_mass, crushing_capacity, "sulphide"):
            effective_feed_mass = crushing_capacity
        else:
            effective_feed_mass = feed_mass
            
        crushed_mass = effective_feed_mass * crushing_efficiency
        crushed_cu = feed_cu * (effective_feed_mass / feed_mass) * crushing_efficiency
        crushed_pd = feed_pd * (effective_feed_mass / feed_mass) * crushing_efficiency
        crushed_pt = feed_pt * (effective_feed_mass / feed_mass) * crushing_efficiency
        crushed_au = feed_au * (effective_feed_mass / feed_mass) * crushing_efficiency
        crushed_ni = feed_ni * (effective_feed_mass / feed_mass) * crushing_efficiency
        crushed_co = feed_co * (effective_feed_mass / feed_mass) * crushing_efficiency
        crushing_losses = effective_feed_mass - crushed_mass
        
        # Stage 3: Grinding
        grinding_efficiency = self.process_params['sulphide_grinding_efficiency'] / 100
        grinding_capacity = crushed_mass * 0.95  # Grinding is often the bottleneck
        
        if not self.validate_material_flow("Grinding", crushed_mass, grinding_capacity, "sulphide"):
            effective_crushed_mass = grinding_capacity
            grinding_efficiency_adjusted = grinding_efficiency * 0.92  # Reduced efficiency when overloaded
        else:
            effective_crushed_mass = crushed_mass
            grinding_efficiency_adjusted = grinding_efficiency
            
        ground_mass = effective_crushed_mass * grinding_efficiency_adjusted
        ground_cu = crushed_cu * (effective_crushed_mass / crushed_mass) * grinding_efficiency_adjusted
        ground_pd = crushed_pd * (effective_crushed_mass / crushed_mass) * grinding_efficiency_adjusted
        ground_pt = crushed_pt * (effective_crushed_mass / crushed_mass) * grinding_efficiency_adjusted
        ground_au = crushed_au * (effective_crushed_mass / crushed_mass) * grinding_efficiency_adjusted
        ground_ni = crushed_ni * (effective_crushed_mass / crushed_mass) * grinding_efficiency_adjusted
        ground_co = crushed_co * (effective_crushed_mass / crushed_mass) * grinding_efficiency_adjusted
        grinding_losses = effective_crushed_mass - ground_mass
        
        # Stage 4: Copper Flotation
        cu_flotation_efficiency = self.process_params['cu_flotation_efficiency'] / 100
        cu_flotation_recovery = self.process_params['cu_flotation_recovery'] / 100
        pgm_to_cu_concentrate = self.process_params['pgm_to_cu_concentrate'] / 100
        
        cu_flotation_capacity = ground_mass * 1.1  # Flotation capacity
        
        if not self.validate_material_flow("Cu Flotation", ground_mass, cu_flotation_capacity, "sulphide"):
            effective_ground_mass = cu_flotation_capacity
        else:
            effective_ground_mass = ground_mass
        
        # Copper concentrate mass and metals
        cu_concentrate_mass = effective_ground_mass * 0.15  # Typical concentrate yield
        cu_in_concentrate = ground_cu * (effective_ground_mass / ground_mass) * cu_flotation_recovery
        pd_in_cu_concentrate = ground_pd * (effective_ground_mass / ground_mass) * pgm_to_cu_concentrate
        pt_in_cu_concentrate = ground_pt * (effective_ground_mass / ground_mass) * pgm_to_cu_concentrate
        au_in_cu_concentrate = ground_au * (effective_ground_mass / ground_mass) * pgm_to_cu_concentrate
        
        # Remaining material after Cu flotation
        remaining_after_cu = effective_ground_mass - cu_concentrate_mass
        remaining_pd = ground_pd * (effective_ground_mass / ground_mass) - pd_in_cu_concentrate
        remaining_pt = ground_pt * (effective_ground_mass / ground_mass) - pt_in_cu_concentrate
        remaining_au = ground_au * (effective_ground_mass / ground_mass) - au_in_cu_concentrate
        remaining_ni = ground_ni * (effective_ground_mass / ground_mass)
        remaining_co = ground_co * (effective_ground_mass / ground_mass)
        
        # Stage 5: Nickel Flotation
        ni_flotation_efficiency = self.process_params['ni_flotation_efficiency'] / 100
        ni_flotation_recovery = self.process_params['ni_flotation_recovery'] / 100
        co_flotation_recovery = self.process_params['co_flotation_recovery'] / 100
        pgm_to_ni_concentrate = self.process_params['pgm_to_ni_concentrate'] / 100
        
        ni_flotation_capacity = remaining_after_cu * 1.05
        
        if not self.validate_material_flow("Ni Flotation", remaining_after_cu, ni_flotation_capacity, "sulphide"):
            effective_remaining_mass = ni_flotation_capacity
        else:
            effective_remaining_mass = remaining_after_cu
        
        # Nickel concentrate
        ni_concentrate_mass = effective_remaining_mass * 0.20  # Typical concentrate yield
        ni_in_concentrate = remaining_ni * (effective_remaining_mass / remaining_after_cu) * ni_flotation_recovery
        co_in_concentrate = remaining_co * (effective_remaining_mass / remaining_after_cu) * co_flotation_recovery
        pd_in_ni_concentrate = remaining_pd * (effective_remaining_mass / remaining_after_cu) * pgm_to_ni_concentrate
        pt_in_ni_concentrate = remaining_pt * (effective_remaining_mass / remaining_after_cu) * pgm_to_ni_concentrate
        au_in_ni_concentrate = remaining_au * (effective_remaining_mass / remaining_after_cu) * pgm_to_ni_concentrate
        
        # Tailings after flotation
        flotation_tailings = effective_remaining_mass - ni_concentrate_mass
        
        # Stage 6: Pressure Oxidation
        pressure_ox_efficiency = self.process_params['pressure_oxidation_efficiency'] / 100
        pressure_ox_capacity = (cu_concentrate_mass + ni_concentrate_mass) * 1.02
        
        total_concentrate = cu_concentrate_mass + ni_concentrate_mass
        if not self.validate_material_flow("Pressure Oxidation", total_concentrate, pressure_ox_capacity, "sulphide"):
            pressure_ox_efficiency = pressure_ox_efficiency
