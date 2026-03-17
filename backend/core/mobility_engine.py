import time
import random

class MobilityEngine:
    def __init__(self):
        self.knowledge_base = [
            {"query": "What is the fastest route to the city center?", "answer": "The fastest route is via the North Expressway, taking approximately 25 minutes in current traffic."},
            {"query": "Show me eco-friendly travel options to the airport.", "answer": "The most sustainable option is the electric shuttle train, which reduces carbon emissions by 85% compared to driving."},
            {"query": "How can I avoid traffic during rush hour?", "answer": "Consider using the dedicated bike lanes or the metro line 3 to bypass the congested downtown corridors."},
            {"query": "What are the best public transport routes for commuting?", "answer": "The rapid transit bus service (Line A) offers the most frequent and reliable commute, with departures every 5 minutes."},
            {"query": "Is there a green way to travel across town?", "answer": "You can use the city's integrated e-bike sharing program, which has 500+ stations across all major districts."},
            {"query": "Find the quickest path to the shopping mall.", "answer": "Taking the 4th Street tunnel is currently 10 minutes faster than the surface roads due to roadwork on Main St."},
            {"query": "Environmentally friendly ways to get to the stadium.", "answer": "A special 'Go Green' shuttle service runs from the Central Station on game days, using 100% bio-fuel."},
            {"query": "Cheapest way to reach the suburban area.", "answer": "The regional commuter rail is the most cost-effective, with weekend passes offering significant discounts."},
            {"query": "Cycling routes with the least elevation.", "answer": "The Riverside Path is predominantly flat and offers a scenic, low-effort route across the city."},
            {"query": "Real-time traffic updates for the southern highway.", "answer": "Current reports show a 15-minute delay near the bridge; consider taking the bypass exit 14."},
            {"query": "How to get to the museum using only electric vehicles?", "answer": "The EV-exclusive car-sharing zone near your location has 5 cars available for a direct trip to the museum."},
            {"query": "Best walking paths for a 15-minute commute.", "answer": "The Greenway pedestrian corridor connects the residential zone to the business district in exactly 12 minutes."},
            {"query": "Are there any shared mobility options nearby?", "answer": "There are 3 carpool groups leaving from the neighborhood hub within the next 30 minutes."},
            {"query": "Map out a low-carbon route to the university.", "answer": "Combining the metro with a short walk through the University Park is the lowest emission path available."},
            {"query": "Most reliable transport during heavy rain?", "answer": "The underground subway system (Metro Lines 1 & 2) remains unaffected by weather conditions and follows a strict schedule."},
            {"query": "Compare driving vs. transit time to the port.", "answer": "Driving takes 40 minutes with current congestion, while the express ferry takes only 30 minutes."},
            {"query": "Wheelchair accessible routes to the park.", "answer": "All 'CityLink' buses on Route 45 are fully accessible and drop off directly at the park's main entrance."},
            {"query": "Find a route that avoids the construction on 5th Ave.", "answer": "Divert via 7th Avenue to avoid the 'no-entry' zone between King St and Queen St."},
            {"query": "What is the energy consumption of taking the train?", "answer": "The inter-city train consumes approximately 0.15 kWh per passenger-kilometer, making it highly efficient."},
            {"query": "Suggest a scenic but fast route to the lookout point.", "answer": "The Skyway Drive offers breathtaking views and is only 5 minutes longer than the industrial bypass."},
            {"query": "Where can I park my electric scooter safely?", "answer": "The smart-docking stations at every metro entrance offer secure parking and integrated charging for e-scooters."},
            {"query": "Is there a carpooling service for the tech park?", "answer": "Yes, 'TechRide' is a dedicated app for employees to coordinate carpools to the northern tech campus."},
            {"query": "Most scenic bike path to the library.", "answer": "The Lakeside Loop is highly recommended; it adds only 2km to your trip but is completely car-free."},
            {"query": "How to reduce my carbon footprint while traveling?", "answer": "Prioritize active transport (walking/cycling) or electrified public transit over private fossil-fuel vehicles."},
            {"query": "Last train timings from the central station.", "answer": "The final trains on all major lines depart at 12:30 AM on weekdays and 1:30 AM on weekends."},
            {"query": "Availability of handicap parking at the town hall.", "answer": "There are 12 dedicated spots in the underground garage, with elevator access directly to the main lobby."},
            {"query": "Fastest way to get home during the parade?", "answer": "The parade blocks the surface streets; use the Metro or the perimeter ring road for the best results."},
            {"query": "How do I use the new integrated mobility app?", "answer": "Scan the QR code at any transit stop to download the app and manage all your transport bookings in one place."},
            {"query": "Incentives for using sustainable transport today.", "answer": "Today is 'Green Transit Day'; all bus and tram rides are free between 10 AM and 4 PM."},
            {"query": "Optimal route to the hospital avoiding the fairgrounds.", "answer": "The East Bypass avoids the heavy crowds and traffic around the fairgrounds, saving you 20 minutes."}
        ]

    def process_query(self, query: str):
        # Simulate processing delay
        delay = random.uniform(0.5, 1.5)
        time.sleep(delay)
        
        # In a real system, this would call an LLM or Route API
        # Here we mimic it by finding the best keyword match in our 30 queries
        # If no good match, we return a fallback response
        query_lower = query.lower()
        best_match = None
        max_overlap = 0

        for item in self.knowledge_base:
            overlap = len(set(query_lower.split()) & set(item['query'].lower().split()))
            if overlap > max_overlap:
                max_overlap = overlap
                best_match = item

        if best_match and max_overlap > 1:
            ans = best_match['answer']
        else:
            ans = f"Analyzed your request: '{query}'. The optimal path involves a combination of express transit and micro-mobility to ensure sustainability."

        return {
            'mode': 'Smart Recommendation',
            'description': ans,
            'estimated_time': f"{random.randint(15, 60)} mins",
            'carbon_footprint': f"{random.uniform(0.2, 4.0):.1f} kg CO2",
            'engine_latency': round(delay, 2)
        }
