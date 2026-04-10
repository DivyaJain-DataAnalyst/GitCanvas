def draw_sparkline(data, color="#58a6ff"):
    if not data or sum(data) == 0:
        data = [2, 6, 4, 10, 5, 12, 8, 15, 10, 18, 12, 20, 15]

    width, height, padding = 400, 100, 20
    max_val = max(data) if max(data) > 0 else 1
    
    pts = []
    for i, val in enumerate(data):
        x = (i / (len(data) - 1)) * width
        y = (height - padding) - (val / max_val * (height - 2 * padding))
        pts.append(f"{x},{y}")
    
    path_str = "L".join(pts)
    line_path = f"M{path_str}"
    area_path = f"M0,{height} L{path_str} L{width},{height} Z"

    # Generate circles with staggered delays and a "ping" pulse
    circles = []
    for i, p in enumerate(pts):
        delay = 0.5 + (i * 0.08)
        x, y = p.split(",")
        circles.append(f'''
            <g class="node-group" style="animation-delay: {delay:.2f}s;">
                <circle class="node-ping" cx="{x}" cy="{y}" r="3" fill="{color}" />
                <circle class="node" cx="{x}" cy="{y}" r="3.5" fill="{color}" />
            </g>
        ''')

    return f'''
    <svg width="100%" height="{height}" viewBox="0 0 {width} {height}" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
        <style>
            @keyframes drawLine {{
                from {{ stroke-dashoffset: 1000; }}
                to {{ stroke-dashoffset: 0; }}
            }}
            @keyframes popNode {{
                0% {{ transform: scale(0); opacity: 0; }}
                70% {{ transform: scale(1.6); opacity: 1; }}
                100% {{ transform: scale(1); opacity: 1; }}
            }}
            @keyframes ping {{
                0% {{ transform: scale(1); opacity: 0.8; }}
                100% {{ transform: scale(3.5); opacity: 0; }}
            }}
            @keyframes pulseWave {{
                0% {{ transform: translateX(-100%); }}
                100% {{ transform: translateX(100%); }}
            }}
            @keyframes flicker {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.7; }}
                80% {{ opacity: 0.9; }}
            }}
            
            .grid-line {{
                stroke: {color};
                stroke-opacity: 0.05;
                stroke-width: 0.5;
            }}

            .base-line {{
                stroke: {color};
                stroke-opacity: 0.15;
                stroke-width: 1;
                stroke-dasharray: 2,4;
            }}
            
            .main-line {{
                stroke: {color};
                stroke-width: 3;
                fill: none;
                stroke-dasharray: 1000;
                stroke-dashoffset: 1000;
                stroke-linecap: butt;
                stroke-linejoin: miter;
                animation: drawLine 2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
                filter: drop-shadow(0 0 2px {color}) drop-shadow(0 0 6px {color});
            }}
            
            .node-group {{
                opacity: 0;
                transform-origin: center;
                animation: popNode 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
            }}
            
            .node {{
                filter: drop-shadow(0 0 4px {color});
                animation: flicker 2s infinite;
            }}
            
            .node-ping {{
                animation: ping 1.5s ease-out infinite;
                animation-delay: inherit;
            }}
            
            .area-fill {{
                fill: {color};
                fill-opacity: 0.08;
            }}
            
            .pulse-container {{
                mask: url(#path-mask);
            }}
            
            .scanner {{
                animation: pulseWave 3s cubic-bezier(0.4, 0, 0.2, 1) infinite;
                opacity: 0.5;
            }}
            
            .scan-bar {{
                width: 2px;
                height: {height}px;
                fill: {color};
                filter: drop-shadow(0 0 8px {color});
                animation: pulseWave 3s cubic-bezier(0.4, 0, 0.2, 1) infinite;
            }}
        </style>
        
        <defs>
            <linearGradient id="pulse-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="{color}" stop-opacity="0" />
                <stop offset="50%" stop-color="{color}" stop-opacity="0.8" />
                <stop offset="100%" stop-color="{color}" stop-opacity="0" />
            </linearGradient>
            
            <mask id="path-mask">
                <path d="{area_path}" fill="white" />
            </mask>
        </defs>

        <!-- Subtle Grid -->
        <line class="grid-line" x1="0" y1="20" x2="{width}" y2="20" />
        <line class="grid-line" x1="0" y1="40" x2="{width}" y2="40" />
        <line class="grid-line" x1="0" y1="60" x2="{width}" y2="60" />
        <line class="grid-line" x1="0" y1="80" x2="{width}" y2="80" />

        <!-- Zero Baseline -->
        <line class="base-line" x1="0" y1="80" x2="{width}" y2="80" />
        
        <!-- Background Area Fill -->
        <path class="area-fill" d="{area_path}" />
        
        <!-- Pulse Wave Layer -->
        <g class="pulse-container">
            <rect class="scanner" width="120" height="{height}" fill="url(#pulse-grad)" />
        </g>
        
        <!-- Scanning Bar -->
        <rect class="scan-bar" x="-2" y="0" width="2" height="{height}" />
        
        <!-- Main Activity Path -->
        <path class="main-line" d="{line_path}" />

        <!-- Data Nodes -->
        {" ".join(circles)}
    </svg>
    '''