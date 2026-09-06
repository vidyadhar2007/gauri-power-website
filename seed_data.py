import os
from datetime import datetime, timezone, timedelta, date
from app import create_app
from models import db, User, DealerProfile, CustomerProfile, Product, QuotationRequest, Quotation, Order, Invoice, Notification

app = create_app()

def seed_database():
    with app.app_context():
        db.create_all()

        # Check if already seeded
        if Product.query.first():
            print("Database already contains product data.")
            return

        print("Seeding authentic Gauri Power catalogue products...")

        products_data = [
            # --- DIVISION 1: SERVO VOLTAGE STABILIZERS & POWER QUALITY (MANUFACTURED) ---
            {
                'slug': 'automatic-servo-voltage-stabilizer',
                'name': 'Automatic 3-Phase Oil-Cooled Servo Voltage Stabilizer',
                'category': 'Servo Voltage Stabilizers',
                'short_description': 'Heavy-duty industrial linear copper strip servo voltage stabilizer with vertical rolling contacts, radiator cooling, and digital micro-controller control.',
                'full_description': 'Gauri Power Automatic 3-Phase Servo Voltage Stabilizers are engineered for continuous 100% duty cycle operation under extreme industrial voltage fluctuations. Utilizing vertical linear rolling contact regulators wound with electrolytic rectangular copper strips (minimum 24 mm² section) instead of ordinary wire dimmers, and prime CRGO laminations. Fitted with self-lubricating graphite carbon roller assemblies that operate for 8 to 10 years maintenance-free without copper track wear.',
                'capacity_range': '30 kVA to 6000 kVA (3500 kVA standard heavy unit)',
                'voltage_range': 'Input: 300-460V, 320-460V, 340-460V, 350-460V (3-Phase) | Output: 400V/415V +/- 1%',
                'efficiency': '> 99.2% (Ultra-low losses 0.5% - 1.2%)',
                'warranty': '5 Years Warranty in India',
                'cooling_type': 'Oil Cooled (Heavy-Duty Radiators Fitted)',
                'duty_cycle': '100% Continuous Duty Cycle',
                'is_featured': True,
                'image_url': 'images/product_balanced_3500kva.jpg',
                'salient_features': [
                    'Zero copper track wear with self-lubricating graphite carbon rollers (8-10 yrs life)',
                    'Heavy rectangular electrolytic copper strips (>= 24 mm² section)',
                    'Superior energy efficiency exceeding 99.2% across full loading range',
                    'Independent digital microcontroller AVR card for accurate RMS voltage sensing',
                    'Full protection: high/low voltage cut-off, single phasing prevention, overload trip',
                    'Vacuum pressure impregnated (VPI) buck-boost core assembly'
                ],
                'technical_specs': {
                    'Input Voltage Range': '300-460V / 320-460V / 340-460V / 350-460V (3-Phase, 50 Hz)',
                    'Output Voltage': '400V / 415V +/- 1% (Adjustable 380V - 425V)',
                    'Correction Rate': '10 to 20 Volts / Second',
                    'Waveform Distortion': 'Virtually Nil (Zero harmonic injection)',
                    'Insulation Class': 'Class A (Oil Immersed)',
                    'Cooling Type': 'Oil Natural Air Natural (ONAN) with external radiator banks',
                    'Mounting': 'Bi-directional / Uni-directional heavy steel rollers'
                },
                'applications': [
                    'Heavy Engineering & Manufacturing Plants', 'Textile & Spinning Mills',
                    'Flour & Rice Mills', 'Chemical & Pharmaceutical Units',
                    'Steel Rolling Mills & Foundries', 'Cold Storage & Food Processing'
                ]
            },
            {
                'slug': 'air-cooled-servo-stabilizer',
                'name': 'Precision 3-Phase Air-Cooled Servo Voltage Stabilizer',
                'category': 'Servo Voltage Stabilizers',
                'short_description': 'Compact, zero-oil air-cooled automatic voltage stabilizer engineered for indoor commercial, CNC, medical, and automated industrial environments.',
                'full_description': 'Gauri Power Air-Cooled Servo Voltage Stabilizers deliver rapid, reliable voltage stabilization without the need for oil servicing. Utilizing precision-wound copper coils, ultra-quiet AC synchronous servomotors, and micro-controller digital control. Ideal for indoor cleanroom facilities, robotic cells, high-speed printing, and computerized CNC machining centers.',
                'capacity_range': '10 kVA to 500 kVA',
                'voltage_range': 'Input: 340-460V / 300-470V | Output: 400V/415V +/- 1%',
                'efficiency': '> 98.8%',
                'warranty': '5 Years Warranty in India',
                'cooling_type': 'Air Cooled (Forced Low-Noise Industrial Exhaust Fans)',
                'duty_cycle': '100% Continuous Duty Rating',
                'is_featured': True,
                'image_url': 'images/product_avr_750kva.jpg',
                'salient_features': [
                    'Zero oil requirement - clean, fire-safe indoor installation',
                    'High-torque low-inertia AC synchronous servomotor drive',
                    'Digital LCD display showing Input/Output Phase voltages and Load current',
                    'Fast response speed with electronic dynamic braking',
                    'Compact modular footprint with caster wheels for easy indoor relocation'
                ],
                'technical_specs': {
                    'Input Voltage Range': '340V - 460V / 300V - 470V (3 Phase 4 Wire)',
                    'Output Voltage': '400V / 415V +/- 1% stabilized',
                    'Response Time': '< 20 milliseconds',
                    'Correction Speed': '20 to 35 Volts / Second',
                    'Protection': 'Under/Over voltage trip, Time delay relay, Overload protection',
                    'Enclosure': 'Sheet steel IP21 / IP31 powder-coated enclosure'
                },
                'applications': [
                    'CNC Machinery & Robotic Automation', 'Medical Diagnostic & Imaging Equipment',
                    'Commercial Printing & Packaging Units', 'IT Data Centers & Server Rooms',
                    'Research Laboratories', 'Automobile Ancillaries'
                ]
            },
            {
                'slug': 'ht-servo-voltage-regulator',
                'name': 'High Tension (HT) Automatic Servo Voltage Regulator',
                'category': 'HT Stabilizers',
                'short_description': 'Direct high-tension 11 kV / 33 kV substation voltage regulator protecting entire industrial plants right at the incoming grid feeder.',
                'full_description': 'Engineered and manufactured to stabilize erratic high-tension incoming supply directly at the 11 kV or 33 kV substation level. Regulates grid fluctuations before power enters plant step-down substations and machinery, drastically cutting plant-wide core and iron losses and ensuring balanced voltage across all downstream machinery.',
                'capacity_range': '500 kVA to 5000 kVA',
                'voltage_range': 'Input: 11 kV / 33 kV (+/- 15% to 20%) | Output: 11 kV / 433V Stable (+/- 1%)',
                'efficiency': '> 99.4%',
                'warranty': '5 Years Warranty in India',
                'cooling_type': 'ONAN (Oil Natural Air Natural)',
                'duty_cycle': '100% Continuous Substation Duty',
                'is_featured': True,
                'image_url': 'images/product_servo_stabilizer_large.jpg',
                'salient_features': [
                    'Centralized plant voltage stabilization directly at 11kV or 33kV incoming feeder',
                    'Drastic reduction in plant motor burnouts and equipment failure',
                    'Heavy motorized linear rolling contact regulation mechanism',
                    'High dielectric strength insulating mineral oil with conservator and silica gel breather',
                    'Buchholz relay and magnetic oil level gauge protection'
                ],
                'technical_specs': {
                    'Incoming Voltage': '11,000 V / 33,000 V (+/- 15% or +/- 20%)',
                    'Output Voltage': '11,000 V +/- 1% (or direct stepped down 433 V +/- 1%)',
                    'Frequency': '50 Hz +/- 3%',
                    'Insulation Level': 'Class A (Oil Immersed, BIL 75 kVp / 170 kVp)',
                    'Vector Group': 'Dyn11 (for combined HT/LT units)',
                    'Radiators': 'Pressed steel flanged detachable radiators'
                },
                'applications': [
                    'Large Continuous Process Factories', 'Cement & Clinker Grinding Plants',
                    'Induction Furnace & Steel Rolling Mills', 'Paper & Pulp Mills',
                    'Industrial Substation Feeders'
                ]
            },
            {
                'slug': 'linear-roller-servo-stabilizer',
                'name': 'Heavy Copper Strip Linear Rolling Contact Servo Stabilizer',
                'category': 'Servo Voltage Stabilizers',
                'short_description': 'Vertical linear track voltage regulator with self-lubricating graphite carbon rollers and heavy rectangular copper conductors.',
                'full_description': 'Custom-engineered by Gauri Power for continuous heavy manufacturing plants where conventional wire-wound stabilizers suffer carbon brush burnout. Replaces conventional round wire dimmers with heavy rectangular copper strips and heavy-duty carbon rollers that roll smoothly across copper tracks without pitting, sparking, or wear.',
                'capacity_range': '100 kVA to 6000 kVA',
                'voltage_range': 'Input: 240-480V / 300-460V (3-Phase) | Output: 400V/415V +/- 1%',
                'efficiency': '> 99.3%',
                'warranty': '5 Years Warranty in India',
                'cooling_type': 'Oil Cooled with Heavy-Duty Corrugated Radiator Fins',
                'duty_cycle': '100% Continuous Duty Rating',
                'is_featured': True,
                'image_url': 'images/product_linear_roller_servo.jpg',
                'salient_features': [
                    'Patented rolling carbon mechanism with zero copper friction and zero wear',
                    'Rectangular electrolytic copper strip windings (up to 150 mm² cross-section)',
                    'Zero pitting or carbon residue buildup in insulating oil',
                    'Massive inrush withstand capability for high-starting-torque electric motors',
                    'Designed for 24/7/365 uninterrupted production environments'
                ],
                'technical_specs': {
                    'Conductor Type': '99.99% Electrolytic Pure Rectangular Copper Strip',
                    'Contact System': 'Spring-loaded self-lubricating graphite carbon roller assemblies',
                    'Input Voltage': '240V - 480V or 300V - 460V (3-Phase)',
                    'Output Voltage': '415V +/- 1%',
                    'Temperature Rise': '< 45 °C over ambient at 100% continuous full load',
                    'Duty': 'Unrestricted continuous industrial operation'
                },
                'applications': [
                    'Heavy Forging & Foundry Plants', 'Plastic Injection Molding & Extrusion',
                    'Continuous Chemical Reaction Vessels', 'Heavy Machine Tool Manufacturing',
                    'Grain Processing & Modern Rice Mills'
                ]
            },
            {
                'slug': 'single-phase-servo-stabilizer',
                'name': 'Precision Single-Phase Automatic Servo Voltage Stabilizer',
                'category': 'Servo Voltage Stabilizers',
                'short_description': 'Fast-response single-phase voltage regulator for specialized laboratory, IT, medical, and commercial equipment.',
                'full_description': 'Engineered with precision microcontroller AVR circuitry to maintain absolute 230V +/- 1% output across wide single-phase utility fluctuations. Eliminates dangerous voltage sags, brownouts, and surges that damage sensitive scientific instruments and electronics.',
                'capacity_range': '3 kVA to 50 kVA',
                'voltage_range': 'Input: 160-260V / 140-280V / 90-280V | Output: 230V +/- 1%',
                'efficiency': '> 98.5%',
                'warranty': '5 Years Warranty in India',
                'cooling_type': 'Air Cooled / Natural Convection',
                'duty_cycle': '100% Continuous Rating',
                'is_featured': False,
                'image_url': 'images/product_residential_commercial.jpg',
                'salient_features': [
                    'Microprocessor closed-loop control system',
                    'Fast response with electronic braking preventing hunting and overshoot',
                    'High & low voltage cut-off protection with programmable time delay',
                    'Pure sine wave output with zero distortion',
                    'Compact aesthetic design suitable for indoor lab and office placement'
                ],
                'technical_specs': {
                    'Input Voltage': '160V - 260V / 140V - 280V / 90V - 280V (Single Phase, 50 Hz)',
                    'Output Voltage': '230V +/- 1% (Adjustable 220V - 240V)',
                    'Waveform Distortion': 'Nil',
                    'Frequency': '47 Hz - 53 Hz',
                    'Display': 'Digital voltmeter & ammeter with status indicators'
                },
                'applications': [
                    'Analytical & Medical Laboratories', 'Printing Presses & Photocopiers',
                    'Commercial Telecom & Broadcast Towers', 'Residential Villas & Commercial Offices'
                ]
            },
            {
                'slug': 'unbalanced-load-servo-stabilizer',
                'name': 'Independent Phase Control Unbalanced Load Servo Stabilizer',
                'category': 'Servo Voltage Stabilizers',
                'short_description': 'Three independent motorized drive and sensing channels delivering balanced 415V even with 100% unbalanced loads.',
                'full_description': 'In modern manufacturing facilities, mixed single-phase and three-phase loads frequently lead to severe phase voltage imbalance. This specialized stabilizer incorporates 3 individual control cards, 3 servomotors, and 3 independent linear regulators to regulate each phase relative to neutral independently.',
                'capacity_range': '50 kVA to 3000 kVA',
                'voltage_range': 'Input: 300-470V Phase-to-Phase (Unbalanced) | Output: 415V +/- 1% (Phase-to-Phase Balanced)',
                'efficiency': '> 99%',
                'warranty': '5 Years Warranty in India',
                'cooling_type': 'Oil Cooled (Radiator Tanked)',
                'duty_cycle': '100% Continuous',
                'is_featured': False,
                'image_url': 'images/product_avr_550kva.jpg',
                'salient_features': [
                    'Three independent motorized drive systems for R, Y, and B phases',
                    'Delivers balanced 415V line-to-line output even with 100% load imbalance',
                    'True RMS independent voltage sensing on all 3 phases',
                    'Eliminates neutral current overheating caused by phase asymmetry',
                    'Individual phase digital meters for comprehensive real-time diagnostics'
                ],
                'technical_specs': {
                    'Control Mechanism': '3 Independent micro-controllers with individual servo drive assemblies',
                    'Input Voltage': '300V - 470V Line-to-Line (with extreme phase imbalance)',
                    'Output Voltage': '415V +/- 1% Line-to-Line, 240V +/- 1% Line-to-Neutral',
                    'Correction Rate': '15 to 25 Volts / Second per phase',
                    'Unbalance Capability': 'Can tolerate 100% load unbalance and 100% supply unbalance'
                },
                'applications': [
                    'Textile Weaving & Dyeing Mills', 'Multi-Tenant Industrial Parks',
                    'Automotive Assembly Plants', 'Commercial Towers & IT Parks',
                    'Food Processing & Packaging Plants'
                ]
            },
            {
                'slug': 'ultra-wide-input-servo-stabilizer',
                'name': 'Ultra-Wide Input Range (170V-480V) Heavy Industrial Servo Stabilizer',
                'category': 'Servo Voltage Stabilizers',
                'short_description': 'Oil-cooled linear copper strip servo stabilizer engineered for extreme voltage dips down to 170V and surges up to 480V in remote and rural industrial belts.',
                'full_description': 'Manufactured at Gauri Power\'s Ropar works to conquer extreme utility supply instability where standard stabilizers trip or burn out. Incorporates an oversized high-ratio series buck-boost transformer, prime M4 CRGO silicon steel operating at conservative magnetic flux density (< 1.6 Tesla), and heavy linear rectangular copper strips (>= 24 mm² section) with self-lubricating graphite carbon rollers.',
                'capacity_range': '50 kVA to 3000 kVA',
                'voltage_range': 'Input: 170V-480V / 200V-500V (3-Phase) | Output: 400V/415V +/- 1%',
                'efficiency': '> 99% across wide dynamic input swing',
                'warranty': '5 Years Warranty in India',
                'cooling_type': 'Oil Cooled with Heavy External Radiators (ONAN)',
                'duty_cycle': '100% Continuous Duty Rating',
                'is_featured': False,
                'image_url': 'images/product_ultra_wide_servo.jpg',
                'salient_features': [
                    'Exceptional operating range: handles acute voltage drops to 170V and surges to 480V/500V',
                    'Oversized buck-boost transformer preventing saturation under low-voltage high-current draws',
                    'Linear rectangular copper strip winding with vertical graphite rolling contacts',
                    'Conservator tank with silica-gel dehydrating breather and magnetic oil level gauge',
                    'Multi-parameter digital AVR controller maintaining exact 415V +/- 1% output'
                ],
                'technical_specs': {
                    'Input Voltage Range': '170V - 480V / 200V - 500V Line-to-Line (3-Phase, 50 Hz)',
                    'Output Voltage': '400V / 415V +/- 1% (Adjustable 380V - 430V)',
                    'Correction Speed': '15 to 30 Volts / Second',
                    'Core Flux Density': 'Kept strictly < 1.6 Tesla to prevent saturation at 170V input',
                    'Insulation Class': 'Class F Interlayer Nomex Dielectric Insulation'
                },
                'applications': [
                    'Rural Industrial Feeders & Agro Processing Plants', 'Cold Storage & Rice Milling Belts',
                    'Mining Operations & Stone Crushers', 'Textile Powerlooms in Low-Voltage Belts'
                ]
            },
            {
                'slug': 'smart-iot-servo-stabilizer',
                'name': 'Smart IoT & Touchscreen HMI Microcontroller Servo Voltage Stabilizer',
                'category': 'Servo Voltage Stabilizers',
                'short_description': 'Next-gen industrial servo stabilizer equipped with 7-inch color touchscreen HMI, 32-bit DSP processor, cloud IoT telemetry, and real-time power logging.',
                'full_description': 'Combines heavy-duty linear copper strip voltage regulation with Industry 4.0 connectivity. Features an integrated 7-inch color touchscreen HMI displaying real-time 3-phase voltages, load currents, power factor, frequency, and harmonic distortion (THD). Built-in IoT gateway transmits live diagnostic metrics to mobile apps and plant SCADA systems over Modbus TCP/IP.',
                'capacity_range': '30 kVA to 2500 kVA',
                'voltage_range': 'Input: 340-460V / 300-470V (3-Phase) | Output: 400V/415V +/- 0.5% (High Precision)',
                'efficiency': '> 99.3% with real-time energy loss analytics',
                'warranty': '5 Years Warranty in India',
                'cooling_type': 'Air Cooled / Oil Cooled Options',
                'duty_cycle': '100% Continuous Duty Rating',
                'is_featured': False,
                'image_url': 'images/product_smart_iot_servo.jpg',
                'salient_features': [
                    '7-inch high-definition color touchscreen HMI with user-friendly graphic dashboard',
                    'Real-time monitoring of Phase Voltage, Current, Frequency, PF, kVA, and THD Harmonics',
                    'Built-in IoT gateway with cloud telemetry and automated WhatsApp / SMS fault alerts',
                    'Onboard historical event and fault logging memory (stores up to 10,000 fault records)',
                    'Ultra-precision regulation accuracy calibrated to +/- 0.5% for high-tech robotics & CNC'
                ],
                'technical_specs': {
                    'Processor': '32-Bit High Speed Digital Signal Processor (DSP)',
                    'HMI Interface': '7-inch Industrial Resistive / Capacitive Touchscreen',
                    'Connectivity': 'RS485 Modbus RTU / Ethernet TCP/IP / 4G IoT Gateway',
                    'Regulation Accuracy': '+/- 0.5% (Precision calibrated)',
                    'Power Logging': 'Active Power (kW), Reactive Power (kVAR), Power Factor (PF), THD-V'
                },
                'applications': [
                    'Automated Robotic Manufacturing Cells', 'Semiconductor & Electronics Fabrication',
                    'Pharmaceutical Cleanrooms & R&D Labs', 'High-End CNC & 5-Axis Machining Centers'
                ]
            },
            {
                'slug': 'foundry-rolling-mill-servo-stabilizer',
                'name': 'Severe-Duty Rolling Mill & Induction Furnace Linear Servo Stabilizer',
                'category': 'Servo Voltage Stabilizers',
                'short_description': 'Extra-heavy-duty industrial stabilizer engineered for harsh metallurgical foundry environments, abrasive dust, and 1500% electric motor inrush withstand.',
                'full_description': 'Manufactured to survive in the most punitive industrial operating environments: hot steel rolling mills, induction furnace shops, and chemical processing plants. Constructed with heavy structural ISMC channel base, double-insulated rectangular copper strip windings (>= 35 mm² section), dual external radiator banks, and sealed IP54 control cubicles with internal cooling to prevent dust ingress.',
                'capacity_range': '250 kVA to 6000 kVA',
                'voltage_range': 'Input: 300-460V / 320-480V (3-Phase) | Output: 415V +/- 1%',
                'efficiency': '> 99.2% under extreme cyclical load variations',
                'warranty': '5 Years Warranty in India',
                'cooling_type': 'Heavy-Duty Corrugated Radiators with High-Velocity Forced Fans (ONAN/ONAF)',
                'duty_cycle': '100% Continuous Severe Heavy Industrial Duty',
                'is_featured': False,
                'image_url': 'images/product_foundry_servo.jpg',
                'salient_features': [
                    'Massive 1500% motor starting inrush withstand capability without voltage collapse',
                    'Heavy-gauge structural channel base frame with bi-directional heavy steel rollers',
                    'Double-insulated Class H rectangular copper strips (>= 35 mm² section)',
                    'Dual heavy corrugated cooling radiator banks maintaining oil temperature rise < 40°C',
                    'Sealed IP54 dust-proof control cubicle with internal vortex cooler'
                ],
                'technical_specs': {
                    'Input Voltage Range': '300V - 460V / 320V - 480V (3-Phase, 50 Hz)',
                    'Output Voltage': '415V +/- 1% (adjustable)',
                    'Motor Inrush Withstand': '1500% for 2 seconds, 200% continuous for 1 minute',
                    'Operating Ambient': 'Up to 55 °C continuous ambient temperature',
                    'Radiator System': 'Detachable pressed steel radiators with isolation valves'
                },
                'applications': [
                    'Steel Rolling Mills & Induction Furnaces', 'Heavy Forging & Casting Foundries',
                    'Continuous Rubber & Plastic Extrusion', 'Cement Clinker & Grinding Mills'
                ]
            },
            {
                'slug': 'electroplating-rectifier',
                'name': 'Heavy Duty Industrial Electroplating Rectifier & Regulated DC Unit',
                'category': 'Power Quality & Panels',
                'short_description': 'High-current variable DC regulated power supply engineered for anodizing, electroplating, and metal refining.',
                'full_description': 'Combines Gauri Power precision voltage regulation technology with heavy-duty silicon/thyristor rectification. Hermetically oil-sealed in robust steel tanks to resist corrosive chemical fumes in electroplating, anodizing, and electrowinning operations.',
                'capacity_range': '500 Amps to 20,000 Amps (0-12V / 0-16V / 0-24V / 0-48V DC)',
                'voltage_range': '415V 3-Phase AC Input | 0-12V / 0-24V / 0-48V Stepless DC Output',
                'efficiency': '> 92%',
                'warranty': '5 Years Warranty in India',
                'cooling_type': 'Oil Cooled Hermetic Tank',
                'duty_cycle': '100% Continuous Rating',
                'is_featured': False,
                'image_url': 'images/product_electroplating_rectifier.jpg',
                'salient_features': [
                    'Stepless DC voltage regulation from 0 to rated voltage',
                    'Hermetically sealed oil tank protecting against acidic and corrosive chemical fumes',
                    'Heavy-duty industrial silicon diodes and thyristors with heatsinks',
                    'Electronic fast-acting overload and short-circuit trip protection'
                ],
                'technical_specs': {
                    'Input Voltage': '415 V +/- 10%, 3-Phase, 50 Hz AC',
                    'Output Voltage': '0 - 12V / 16V / 24V / 48V DC continuously variable',
                    'Ripple Factor': '< 5% RMS across full range',
                    'Control': 'Motorized variac control or Thyristor phase angle control',
                    'Metering': 'Digital DC Voltmeter & Ammeter with shunt'
                },
                'applications': [
                    'Hard Chrome & Zinc Plating', 'Anodizing & Electro-Coloring',
                    'Electrowinning & Metal Refining', 'Hydrogen Generation Plants'
                ]
            },
            {
                'slug': 'apfc-harmonic-filter-panel',
                'name': 'Automatic Power Factor Correction (APFC) & Active Harmonic Filter Panel',
                'category': 'Power Quality & Panels',
                'short_description': 'Microprocessor-controlled capacitor bank and detuned reactor panel maintaining near-unity power factor (0.99) and eliminating electricity penalties.',
                'full_description': 'Integrates seamlessly with Gauri Power servo voltage stabilizers to ensure the entire plant power factor stays above 0.98. Incorporates heavy-duty MPP capacitors, copper-wound detuned harmonic reactors (7% or 14%), and intelligent multi-stage numerical power factor controllers.',
                'capacity_range': '50 kVAR to 1500 kVAR',
                'voltage_range': '415V, 3 Phase, 50 Hz',
                'efficiency': '> 99.5%',
                'warranty': '5 Years Warranty in India',
                'cooling_type': 'Forced Air Ventilation with Thermostat Control',
                'duty_cycle': '100% Continuous Rating',
                'is_featured': False,
                'image_url': 'images/product_apfc_panel.jpg',
                'salient_features': [
                    'Microprocessor-based automatic power factor controller with intelligent switching',
                    'Heavy-duty gas-filled / MPP capacitors with self-healing dielectric',
                    'Copper-wound detuned reactors preventing harmonic resonance',
                    'Eliminates low power factor penalties imposed by state electricity distribution utilities',
                    'Thermostatically controlled forced ventilation with louvers and filters'
                ],
                'technical_specs': {
                    'Operating Voltage': '415V (+/- 10%), 3-Phase, 50 Hz',
                    'Steps': '4 to 16 configurable stages with cyclic switching',
                    'Reactors': '7% (189 Hz) or 14% (134 Hz) detuned copper harmonic reactors',
                    'Target Power Factor': '0.98 to 0.99 Lag / Unity',
                    'Enclosure': 'Floor-mounted modular sheet steel IP42 / IP52 panel'
                },
                'applications': [
                    'Heavy Industrial Plants with Non-Linear Loads', 'Induction Furnaces & Foundries',
                    'Commercial Buildings & Hospitals', 'Rice Mills & Agro Processing'
                ]
            },

            # --- DIVISION 2: VACUUM CIRCUIT BREAKERS - VCB (DEALT & SUPPLIED - 100% INDOOR & COMPACT) ---
            {
                'slug': 'indoor-vcb-switchgear-panel',
                'name': '11 kV Indoor Draw-Out Vacuum Circuit Breaker (VCB) Switchgear Panel',
                'category': 'Vacuum Circuit Breakers (VCB)',
                'short_description': 'Metal-clad, compartmentalized 11 kV draw-out vacuum circuit breaker panel with digital numerical protection relay and interlocked racking.',
                'full_description': 'Gauri Power supplies authorized, type-tested 11 kV indoor metal-clad Vacuum Circuit Breakers (VCB). Engineered with sealed ceramic vacuum interrupters, motorized spring-charging mechanisms, comprehensive automatic safety shutters, and microprocessor numerical relays. Extensively supplied to manufacturing plants, continuous process industries, and utility distribution substations across India.',
                'capacity_range': '630A, 1250A, 1600A, 2000A (Breaking Capacity: 26.3 kA / 31.5 kA rms)',
                'voltage_range': 'Rated Voltage: 12 kV / 11 kV | Impulse Withstand: 75 kVp | Power Frequency: 28 kV rms',
                'efficiency': 'Maintenance-free vacuum interrupters rated for 30,000 mechanical operations',
                'warranty': '5 Years Warranty in India',
                'cooling_type': 'Natural Air Cooled within IP4X Metal Enclosure',
                'duty_cycle': 'Rapid Auto-Reclosing Duty (O - 0.3s - CO - 3min - CO)',
                'is_featured': True,
                'image_url': 'images/product_indoor_vcb_panel.jpg',
                'salient_features': [
                    'Hermetically sealed ceramic vacuum interrupters with low contact erosion',
                    'Fully compartmentalized metal-clad steel construction with internal arc classification (IAC)',
                    'Motorized spring-charging mechanism with emergency manual charging handle',
                    'Comprehensive safety interlocks preventing racking under closed breaker conditions',
                    'Digital numerical multi-function protection relay with RS485 / Modbus SCADA compatibility'
                ],
                'technical_specs': {
                    'Rated System Voltage': '11 kV (Maximum 12 kV, 3-Phase, 50 Hz)',
                    'Rated Normal Current': '630A / 1250A / 1600A / 2000A',
                    'Short-Circuit Breaking Current': '26.3 kA / 31.5 kA rms for 3 seconds',
                    'Making Capacity': '66 kA / 78.75 kA peak',
                    'Operating Sequence': 'O - 0.3s - CO - 3min - CO',
                    'Standard Compliance': 'IEC 62271-100 / IEC 62271-200 / IS 13118'
                },
                'applications': [
                    'Industrial Incomer & Outgoing Feeders', 'Substation Switchgear Rooms',
                    'Heavy Manufacturing Facilities', 'Captive Power Plants',
                    'Commercial Complexes & Hospitals'
                ]
            },
            {
                'slug': 'compact-indoor-vcb',
                'name': 'Compact Fixed & Cassette Type 11 kV Vacuum Circuit Breaker',
                'category': 'Vacuum Circuit Breakers (VCB)',
                'short_description': 'Space-saving 11 kV compact fixed and cassette vacuum circuit breaker for modular switchgear cubicles, retrofit upgrades, and motor switching.',
                'full_description': 'Gauri Power supplies authorized ultra-compact 11 kV Vacuum Circuit Breakers designed for installations where space is at a premium. Available in both fixed and cassette-mounted draw-out executions, these compact breakers fit seamlessly into modular switchgear cubicles with widths under 600 mm. Incorporates maintenance-free ceramic vacuum bottles, low-mass high-speed spring charging mechanisms, and high-conductivity copper tulip contacts.',
                'capacity_range': '630A / 1250A (Breaking Capacity: 16 kA / 25 kA / 26.3 kA rms)',
                'voltage_range': '11 kV (Max 12 kV) | Impulse Withstand: 75 kVp | Power Frequency: 28 kV rms',
                'efficiency': 'Ultra-low contact erosion with vacuum interrupters rated for 30,000 mechanical operations',
                'warranty': '5 Years Warranty in India',
                'cooling_type': 'Natural Air Cooled (Cassette Mount)',
                'duty_cycle': '100% Continuous Industrial & Auto-Reclose Duty',
                'is_featured': True,
                'image_url': 'images/product_compact_vcb.jpg',
                'salient_features': [
                    'Ultra-compact design fitting into narrow panel enclosures (< 600 mm width)',
                    'Cassette draw-out or fixed execution for rapid substation retrofitting',
                    'Low-mass spring mechanism ensuring fast arc quenching (< 40 ms)',
                    'High-conductivity copper primary disconnect tulip contacts',
                    'Full mechanical interlocking preventing racking under closed breaker status'
                ],
                'technical_specs': {
                    'Rated System Voltage': '11 kV (Max 12 kV, 3-Phase, 50 Hz)',
                    'Rated Normal Current': '630A / 1250A',
                    'Short-Circuit Breaking Current': '16 kA / 25 kA / 26.3 kA for 3 sec',
                    'Total Break Time': '< 40 ms',
                    'Operating Sequence': 'O - 0.3s - CO - 3min - CO',
                    'Installation Type': 'Fixed or Cassette-mounted draw-out execution'
                },
                'applications': [
                    'Retrofit & Replacement of Obsolete MOCB/OCB Breakers', 'Compact Factory Substation Cubicles',
                    'Motor Switching & Capacitor Bank Control', 'Package Substations & Compact Kiosks'
                ]
            },
            {
                'slug': 'compact-rmu-switchgear',
                'name': '11 kV / 22 kV Compact Ring Main Unit (RMU) with Vacuum Circuit Breaker',
                'category': 'Vacuum Circuit Breakers (VCB)',
                'short_description': 'Extensible and non-extensible compact Ring Main Unit (RMU) featuring vacuum circuit breaker tee-off protection for secondary distribution networks and smart cities.',
                'full_description': 'Gauri Power supplies factory-assembled, compact 11 kV & 22 kV Ring Main Units (RMU) engineered for secondary power distribution networks, commercial hubs, solar farms, and smart city infrastructure. Features a hermetically sealed stainless steel tank (IP67 for live parts) enclosing load break switches (LBS) and vacuum circuit breaker (VCB) protection tee-offs with self-powered numerical relays, ensuring zero environmental sensitivity.',
                'capacity_range': '630A Incomer & Feeder (Breaking Capacity: 20 kA / 21 kA rms for 3 sec)',
                'voltage_range': '11 kV / 22 kV (Rated up to 24 kV) | Impulse Withstand: 95 kVp / 125 kVp',
                'efficiency': 'Hermetically sealed live tank (IP67) with zero gas replenishment required for 30 years',
                'warranty': '5 Years Warranty in India',
                'cooling_type': 'Gas / Solid Insulated Hermetic Tank with Natural Air Cooled Enclosure',
                'duty_cycle': '100% Continuous Distribution Grid Duty',
                'is_featured': True,
                'image_url': 'images/product_compact_rmu.jpg',
                'salient_features': [
                    'Hermetically sealed stainless steel enclosure (IP67) resistant to flooding and humidity',
                    'Integrated vacuum circuit breaker tee-off with self-powered numerical protection relay',
                    'Compact modular dimensions ideal for compact package substations and basements',
                    'Extensible and non-extensible configurations (CCV, CCCV, VVV)',
                    'Motorized automation-ready with remote SCADA RTU integration'
                ],
                'technical_specs': {
                    'Rated Voltage': '11 kV / 22 kV (Max 24 kV, 3-Phase, 50 Hz)',
                    'Rated Normal Current': '630A Busbar and Breaker Feeder',
                    'Short Time Withstand Current': '20 kA / 21 kA rms for 3 seconds',
                    'Internal Arc Classification': 'IAC AFLR 20 kA for 1 second',
                    'Tank Protection Degree': 'IP67 Stainless Steel Live Compartment, IP54 Outer Enclosure',
                    'Insulation Type': 'SF6 Gas-Insulated or Environment-Friendly Solid Dielectric'
                },
                'applications': [
                    'Smart City & Underground Power Distribution', 'Commercial Complexes & High-Rise Buildings',
                    'Solar Parks & Renewable Energy Plants', 'Metro Rail Auxiliary Power Substations'
                ]
            },
            {
                'slug': 'heavy-industrial-vcb-panel',
                'name': '11 kV / 33 kV Double Busbar & Incomer-Buscoupler VCB Switchgear Panel Board',
                'category': 'Vacuum Circuit Breakers (VCB)',
                'short_description': 'Fully compartmentalized metal-clad indoor VCB switchboard panel board with draw-out vacuum circuit breakers, dual busbars, and integrated SCADA telemetry.',
                'full_description': 'Supplied for heavy continuous process factories, large power substations, and critical manufacturing facilities. Features fully segregated metal-clad compartments (busbar, breaker, cable, and low-voltage instrument chambers) with certified Internal Arc Classification (IAC AFLR). Accommodates motorized incomer, buscoupler, and feeder breakers with dual electrical and mechanical interlocks.',
                'capacity_range': '1250A to 3150A (Breaking Capacity: 31.5 kA / 40 kA rms)',
                'voltage_range': '11 kV & 33 kV Systems (Power Frequency Withstand: 28 kV / 70 kV rms)',
                'efficiency': 'Ultra-low busbar contact resistance (< 35 micro-ohms) with silver-plated high-conductivity copper',
                'warranty': '5 Years Warranty in India',
                'cooling_type': 'Natural Air Cooled within Compartmentalized Metal-Clad Enclosure',
                'duty_cycle': 'Continuous 24/7/365 Substation Duty',
                'is_featured': False,
                'image_url': 'images/product_heavy_vcb_panel.jpg',
                'salient_features': [
                    'Four independent segregated compartments with automatic metallic safety shutters',
                    'Internal Arc Classified (IAC AFLR 31.5 kA for 1 second) for ultimate operator safety',
                    'Motorized draw-out trolley racking mechanism with front door closed operation',
                    'Advanced numerical multi-function protection relays (50/51, 50N/51N, 27/59, 81)',
                    'Dual busbar or single busbar sectionalized arrangements for uninterrupted plant supply'
                ],
                'technical_specs': {
                    'Rated System Voltage': '11 kV / 33 kV (3-Phase, 50 Hz)',
                    'Rated Continuous Bus Current': '1250A / 1600A / 2000A / 2500A / 3150A',
                    'Short-Circuit Breaking Current': '31.5 kA / 40 kA rms for 3 seconds',
                    'Short-Circuit Making Peak': '78.75 kA / 100 kA peak',
                    'Degree of Enclosure Protection': 'IP4X (Indoor), IP54 (External doors closed)',
                    'Standard Compliance': 'IEC 62271-200 / IEC 62271-100 / IS 3427'
                },
                'applications': [
                    'Heavy Steel Rolling Mills & Arc Furnaces', 'Chemical & Petrochemical Refineries',
                    'Thermal & Hydro Power Plant Substation Incomers', 'Automobile Manufacturing Plants'
                ]
            },
            {
                'slug': 'indoor-33kv-vcb-panel',
                'name': '33 kV Indoor Metal-Clad Draw-Out Vacuum Circuit Breaker Switchgear Panel',
                'category': 'Vacuum Circuit Breakers (VCB)',
                'short_description': 'Fully compartmentalized metal-clad 33 kV indoor draw-out vacuum circuit breaker panel with digital numerical protection relay and motorized racking.',
                'full_description': 'Gauri Power supplies authorized, type-tested 33 kV indoor metal-clad Vacuum Circuit Breakers (VCB) engineered for main plant incoming substations, continuous process heavy industries, and grid step-down switchgear rooms. Features hermetically sealed ceramic vacuum interrupters, motorized spring-charging mechanisms, comprehensive automatic safety shutters, and microprocessor numerical relays.',
                'capacity_range': '1250A, 1600A, 2000A, 2500A (Breaking Capacity: 31.5 kA / 40 kA rms)',
                'voltage_range': 'Rated Voltage: 33 kV (Max 36 kV) | Lightning Impulse: 170 kVp | Power Frequency: 70 kV rms',
                'efficiency': 'Hermetic vacuum interrupters with ultra-low contact erosion rated for 30,000 mechanical operations',
                'warranty': '5 Years Warranty in India',
                'cooling_type': 'Natural Air Cooled within IP4X Metal Enclosure',
                'duty_cycle': 'Rapid Auto-Reclosing Duty (O - 0.3s - CO - 3min - CO)',
                'is_featured': True,
                'image_url': 'images/product_indoor_33kv_vcb.jpg',
                'salient_features': [
                    'Hermetically sealed ceramic vacuum interrupters with long electrical life',
                    'Internal Arc Classified (IAC AFLR 31.5 kA for 1 sec) for maximum operator safety',
                    'Motorized spring-charging mechanism with emergency manual charging handle',
                    'Comprehensive safety interlocks preventing draw-out racking under load',
                    'Digital numerical multi-function protection relay with RS485 SCADA integration'
                ],
                'technical_specs': {
                    'Rated System Voltage': '33 kV (Max 36 kV, 3-Phase, 50 Hz)',
                    'Rated Continuous Current': '1250A / 1600A / 2000A / 2500A',
                    'Short-Circuit Breaking Current': '31.5 kA / 40 kA rms for 3 seconds',
                    'Short-Circuit Making Peak': '78.75 kA / 100 kA peak',
                    'Operating Sequence': 'O - 0.3s - CO - 3min - CO',
                    'Standard Compliance': 'IEC 62271-100 / IEC 62271-200 / IS 13118'
                },
                'applications': [
                    '33 kV Incomer & Substation Switchgear Rooms', 'Heavy Steel & Rolling Mill Substations',
                    'Chemical & Petrochemical Refineries', 'Solar & Renewable Energy Plant Incomers'
                ]
            }
        ]

        for p_data in products_data:
            db.session.add(Product(**p_data))

        print("Creating demo accounts for Dealer, End Customer, and Sales Staff...")

        # 1. End Customer
        cust_user = User(
            name='Rajesh Sharma',
            email='customer@industrial.com',
            phone='+91-98160-12345',
            role='end_customer'
        )
        cust_user.set_password('Customer@123')
        db.session.add(cust_user)
        db.session.flush()

        cust_profile = CustomerProfile(
            user_id=cust_user.id,
            company_name='Northern Industrial Fabricators Ltd',
            industry_type='Manufacturing',
            gst_number='02AABCH1234F1Z5',
            address_line='Plot 48, Industrial Area Barotiwala',
            city='Solan',
            state='Punjab',
            postal_code='174103',
            country='India'
        )
        db.session.add(cust_profile)

        # 2. Dealer
        dealer_user = User(
            name='Vikram Malhotra',
            email='dealer@powertech.com',
            phone='+91-98780-99887',
            role='dealer'
        )
        dealer_user.set_password('Dealer@123')
        db.session.add(dealer_user)
        db.session.flush()

        dealer_profile = DealerProfile(
            user_id=dealer_user.id,
            company_name='Punjab PowerTech & Automation Distributors',
            gst_number='03AACCP9876K1Z9',
            dealership_code='GPT-DLR-PB-042',
            address_line='SCO 112-114, Phase 7 Industrial Area',
            city='Mohali',
            state='Punjab',
            postal_code='160062',
            country='India',
            territory='Punjab & Chandigarh Tricity Region'
        )
        db.session.add(dealer_profile)

        # 3. Sales Staff (Internal)
        sales_user = User(
            name='Er. Amit Chandel',
            email='sales@gauripower.in',
            phone='+91-81789-80216',
            role='sales_staff'
        )
        sales_user.set_password('Sales@123')
        db.session.add(sales_user)

        # 4. Admin (Internal)
        admin_user = User(
            name='Gauri Power Administrator',
            email='admin@gauripower.in',
            phone='+91-78149-43673',
            role='admin'
        )
        admin_user.set_password('Admin@123')
        db.session.add(admin_user)
        db.session.flush()

        # Seed sample workflow items:
        # Sample RFQ 1: Under Review
        rfq1 = QuotationRequest(
            request_number='GPT-RFQ-20260901-001',
            user_id=cust_user.id,
            customer_name='Rajesh Sharma',
            company_name='Northern Industrial Fabricators Ltd',
            contact_number='+91-98160-12345',
            email='customer@industrial.com',
            address_line='Plot 48, Industrial Area Barotiwala',
            city='Solan',
            state='Punjab',
            postal_code='174103',
            country='India',
            product_category='Servo Voltage Stabilizers',
            input_voltage='340-460V (3 Phase, 50Hz)',
            output_voltage='415V +/- 1%',
            selected_capacity='1000 kVA',
            suggested_transformer='Gauri Power Balanced Servo Stabilizer (1000 kVA)',
            oltc_required='No',
            additional_requirements='Heavy rolling contact regulator with carbon roller assembly required. High ambient industrial shed.',
            status='Pending Sales Review'
        )
        db.session.add(rfq1)

        # Sample RFQ 2: Already Quoted and Accepted into Order!
        rfq2 = QuotationRequest(
            request_number='GPT-RFQ-20260825-004',
            user_id=dealer_user.id,
            customer_name='Vikram Malhotra',
            company_name='Punjab PowerTech & Automation Distributors',
            contact_number='+91-98780-99887',
            email='dealer@powertech.com',
            address_line='SCO 112-114, Phase 7 Industrial Area',
            city='Mohali',
            state='Punjab',
            postal_code='160062',
            country='India',
            product_category='Servo Voltage Stabilizers',
            input_voltage='300-460V',
            output_voltage='400V +/- 1%',
            selected_capacity='3500 kVA',
            suggested_transformer='Gauri Power 3500 kVA Balanced Heavy Servo Controller',
            oltc_required='Yes',
            additional_requirements='Tender project for large textile facility in Ropar industrial belt.',
            status='Quotation Sent'
        )
        db.session.add(rfq2)
        db.session.flush()

        # Official Quotation issued by Sales Dept for RFQ 2
        quote2 = Quotation(
            quotation_number='GPT-QT-20260826-002',
            request_id=rfq2.id,
            user_id=dealer_user.id,
            prepared_by='Er. Amit Chandel (Senior Sales Engineer)',
            base_price=2450000.0,
            tax_percent=18.0,
            tax_amount=441000.0,
            freight_charges=45000.0,
            installation_charges=35000.0,
            total_amount=2971000.0,
            valid_until=date.today() + timedelta(days=25),
            delivery_timeline='3 to 4 weeks from technical sign-off',
            payment_terms='30% advance with Purchase Order, 70% against proforma inspection before dispatch',
            warranty_terms='5 Years Manufacturer Warranty in India',
            commercial_terms='Price includes routine and high-voltage factory test certificates.',
            status='Accepted'
        )
        db.session.add(quote2)
        db.session.flush()

        # Confirmed Order created after Dealer accepted quotation
        order2 = Order(
            order_number='GPT-ORD-20260827-001',
            quotation_id=quote2.id,
            user_id=dealer_user.id,
            status='Under Manufacturing',
            transformer_model='3500 kVA Balanced Heavy Servo Voltage Controller',
            capacity='3500 kVA',
            total_amount=quote2.total_amount,
            dispatch_location='Ropar Manufacturing Plant (Punjab)',
            carrier_details='VRL Logistics Heavy Freight Division',
            tracking_reference='VRL-GPT-88902',
            estimated_delivery=(date.today() + timedelta(days=14)).strftime('%d %B %Y')
        )
        db.session.add(order2)

        # Welcome notifications
        db.session.add(Notification(
            user_id=cust_user.id,
            title='Quotation Request Received',
            message='RFQ GPT-RFQ-20260901-001 for 1000 kVA Stabilizer has been submitted to Gauri Power Sales Department. Status: Pending Sales Review.',
            type='info',
            link_url='/my-requests/GPT-RFQ-20260901-001'
        ))

        db.session.add(Notification(
            user_id=dealer_user.id,
            title='Order in Production: GPT-ORD-20260827-001',
            message='Your 3500 kVA servo stabilizer is currently in Stage 3: Under Manufacturing at our Ropar facility.',
            type='success',
            link_url='/my-orders'
        ))

        db.session.commit()
        print("Database seeded successfully with genuine catalogue data, demo accounts, and sample workflow items!")

if __name__ == '__main__':
    seed_database()
