"""
Map visualization module using Folium
Creates interactive HTML maps showing order allocations
"""

import folium
from folium import plugins
from typing import Dict, List, Any
import random


class MapVisualizer:
    """Creates interactive HTML maps of order allocations"""

    # Color palette for drivers (distinct colors)
    COLORS = [
        '#e6194B', '#3cb44b', '#ffe119', '#4363d8', '#f58231',
        '#911eb4', '#42d4f4', '#f032e6', '#bfef45', '#fabed4',
        '#469990', '#dcbeff', '#9A6324', '#fffac8', '#800000',
        '#aaffc3', '#808000', '#ffd8b1', '#000075', '#a9a9a9'
    ]

    def __init__(self):
        # Center on Singapore
        self.center_lat = 1.3521
        self.center_lng = 103.8198

    def create_allocation_map(
        self,
        allocations: List[Dict],
        unallocated_orders: List[Dict],
        output_file: str = "allocation_map.html"
    ):
        """
        Create an interactive map showing all allocations

        Args:
            allocations: List of driver allocations
            unallocated_orders: List of unallocated orders
            output_file: Output HTML file path
        """
        # Create base map
        m = folium.Map(
            location=[self.center_lat, self.center_lng],
            zoom_start=11,
            tiles='OpenStreetMap'
        )

        # Add title
        title_html = '''
        <div style="position: fixed;
                    top: 10px; left: 50px; width: 400px; height: 90px;
                    background-color: white; border:2px solid grey; z-index:9999;
                    font-size:14px; padding: 10px">
        <h4 style="margin: 0">Smart Delivery Allocator</h4>
        <p style="margin: 5px 0"><strong>Total Allocations:</strong> {}</p>
        <p style="margin: 5px 0"><strong>Drivers Used:</strong> {}</p>
        <p style="margin: 5px 0"><strong>Unallocated:</strong> {}</p>
        </div>
        '''.format(
            sum(len(a["orders"]) for a in allocations),
            len(allocations),
            len(unallocated_orders)
        )
        m.get_root().html.add_child(folium.Element(title_html))

        # Create feature groups for each driver
        driver_groups = {}

        for i, allocation in enumerate(allocations):
            driver = allocation["driver"]
            driver_id = driver.get("driver_id", "Unknown")
            driver_name = driver.get("name", "Unknown")
            orders = allocation.get("orders", [])

            # Assign color
            color = self.COLORS[i % len(self.COLORS)]

            # Create feature group for this driver
            group_name = f"{driver_name} ({driver_id}) - {len(orders)} orders"
            fg = folium.FeatureGroup(name=group_name)

            # Add markers for each order
            for order in orders:
                self._add_order_marker(fg, order, driver, color)

            fg.add_to(m)

        # Add unallocated orders in separate group
        if unallocated_orders:
            unallocated_group = folium.FeatureGroup(
                name=f"⚠️ Unallocated Orders ({len(unallocated_orders)})",
                show=True
            )

            for order in unallocated_orders:
                self._add_unallocated_marker(unallocated_group, order)

            unallocated_group.add_to(m)

        # Add layer control
        folium.LayerControl(collapsed=False).add_to(m)

        # Add legend
        self._add_legend(m, allocations)

        # Save map
        m.save(output_file)
        print(f"✅ Map saved to: {output_file}")

    def _add_order_marker(
        self,
        feature_group: folium.FeatureGroup,
        order: Dict,
        driver: Dict,
        color: str
    ):
        """Add a marker for an allocated order"""
        location = order.get("location", {})
        lat = location.get("lat")
        lng = location.get("lng")

        if not lat or not lng:
            return

        order_id = order.get("order_id", "Unknown")
        address = order.get("address", "Unknown")
        tags = order.get("tags", [])
        pax_count = order.get("pax_count", 0)
        setup_time = order.get("setup_time", "")
        event_type = order.get("event_type", "")

        # Create popup
        popup_html = f"""
        <div style="width: 250px">
            <h4 style="margin: 0 0 5px 0">📦 {order_id}</h4>
            <p style="margin: 3px 0"><strong>Address:</strong> {address}</p>
            <p style="margin: 3px 0"><strong>Setup Time:</strong> {setup_time[11:16] if len(setup_time) > 16 else setup_time}</p>
            <p style="margin: 3px 0"><strong>Event:</strong> {event_type}</p>
            <p style="margin: 3px 0"><strong>Pax:</strong> {pax_count}</p>
            <p style="margin: 3px 0"><strong>Tags:</strong> {', '.join(tags) if tags else 'None'}</p>
            <hr style="margin: 5px 0">
            <p style="margin: 3px 0"><strong>🚚 Driver:</strong> {driver.get('name', 'Unknown')}</p>
            <p style="margin: 3px 0"><strong>ID:</strong> {driver.get('driver_id', 'Unknown')}</p>
        </div>
        """

        # Icon based on tags
        icon = "star" if "vip" in tags else "cutlery"

        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{order_id} - {driver.get('name', 'Unknown')}",
            icon=folium.Icon(color='lightgray', icon_color=color, icon=icon, prefix='fa')
        ).add_to(feature_group)

    def _add_unallocated_marker(
        self,
        feature_group: folium.FeatureGroup,
        order: Dict
    ):
        """Add a marker for an unallocated order"""
        location = order.get("location", {})
        lat = location.get("lat")
        lng = location.get("lng")

        if not lat or not lng:
            return

        order_id = order.get("order_id", "Unknown")
        address = order.get("address", "Unknown")
        tags = order.get("tags", [])
        reason = order.get("unallocation_reason", "Unknown reason")

        # Create popup
        popup_html = f"""
        <div style="width: 250px">
            <h4 style="margin: 0 0 5px 0; color: red">⚠️ {order_id}</h4>
            <p style="margin: 3px 0"><strong>Address:</strong> {address}</p>
            <p style="margin: 3px 0"><strong>Tags:</strong> {', '.join(tags) if tags else 'None'}</p>
            <hr style="margin: 5px 0">
            <p style="margin: 3px 0; color: red"><strong>Unallocated:</strong></p>
            <p style="margin: 3px 0; font-size: 12px">{reason}</p>
        </div>
        """

        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"⚠️ {order_id} - UNALLOCATED",
            icon=folium.Icon(color='red', icon='exclamation-triangle', prefix='fa')
        ).add_to(feature_group)

    def _add_legend(self, m: folium.Map, allocations: List[Dict]):
        """Add a legend to the map"""
        if not allocations:
            return

        legend_html = '''
        <div style="position: fixed;
                    bottom: 50px; right: 50px; width: 200px;
                    background-color: white; border:2px solid grey; z-index:9999;
                    font-size:12px; padding: 10px">
        <h4 style="margin: 0 0 10px 0">Legend</h4>
        <p style="margin: 3px 0">
            <i class="fa fa-star" style="color: black"></i> VIP Orders
        </p>
        <p style="margin: 3px 0">
            <i class="fa fa-cutlery" style="color: black"></i> Regular Orders
        </p>
        <p style="margin: 3px 0">
            <i class="fa fa-exclamation-triangle" style="color: red"></i> Unallocated
        </p>
        <hr style="margin: 10px 0">
        <p style="margin: 3px 0; font-size: 11px">
            <strong>Tip:</strong> Click markers for details.<br>
            Use layer control (top right) to filter drivers.
        </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))


def generate_map_from_results(results: Dict, output_file: str):
    """
    Helper function to generate map from allocation results

    Args:
        results: Allocation results dictionary
        output_file: Output HTML file path
    """
    visualizer = MapVisualizer()

    allocations = results.get("allocations", [])
    unallocated = results.get("unallocated_orders", [])

    if not allocations and not unallocated:
        print("⚠️  No data to visualize")
        return

    visualizer.create_allocation_map(allocations, unallocated, output_file)
