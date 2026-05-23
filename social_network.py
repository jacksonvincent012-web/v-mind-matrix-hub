from collections import deque
import heapq

# ================= STEP 1 =================
class User:
    def __init__(self, user_id, name):
        self.user_id = user_id        
        self.name = name              
        self.friends = set()          
        
    def __repr__(self):
        return f"User({self.user_id}, '{self.name}')"


# ================= STEP 2 =================
def quicksort_users(user_list):
    if len(user_list) <= 1:
        return user_list
    
    pivot = user_list[-1]
    
    left = [x for x in user_list[:-1] if x.user_id < pivot.user_id]
    middle = [x for x in user_list if x.user_id == pivot.user_id]
    right = [x for x in user_list[:-1] if x.user_id > pivot.user_id]
    
    return quicksort_users(left) + middle + quicksort_users(right)


# ================= STEP 3 =================
class SocialGraph:
    def __init__(self):
        self.network = {}  # Hash Map framework: user_id -> User Object

    def add_user(self, user):
        self.network[user.user_id] = user

    def add_friendship(self, id1, id2):
        if id1 in self.network and id2 in self.network:
            self.network[id1].friends.add(id2)
            self.network[id2].friends.add(id1)


# ================= STEP 4 =================
class ActionHistory:
    def __init__(self):
        self.stack = []  # Internal array acting as our LIFO stack

    def log_action(self, action_type, data):
        self.stack.append({"action": action_type, "data": data})

    def undo(self, graph):
        if not self.stack:
            print("\n[System Notice] No operations left to undo.")
            return
        
        last_action = self.stack.pop()
        
        if last_action["action"] == "ADD_FRIEND":
            id1, id2 = last_action["data"]
            if id1 in graph.network and id2 in graph.network:
                graph.network[id1].friends.remove(id2)
                graph.network[id2].friends.remove(id1)
                print(f"\n[Undo Success] Severed friendship between {graph.network[id1].name} and {graph.network[id2].name}.")


# ================= STEP 5 =================
def get_friend_recommendations(user_id, graph):
    if user_id not in graph.network:
        return []

    target_user = graph.network[user_id]
    mutual_counts = {}  # Temporary Hash Map: candidate_id -> count of shared friends
    
    queue = deque([user_id])
    visited = {user_id}
    immediate_friends = target_user.friends

    while queue:
        current_id = queue.popleft()
        current_user = graph.network[current_id]
        
        for friend_id in current_user.friends:
            if friend_id not in visited:
                visited.add(friend_id)
                queue.append(friend_id)
                
                if friend_id != user_id and friend_id not in immediate_friends:
                    candidate_user = graph.network[friend_id]
                    shared_friends = immediate_friends.intersection(candidate_user.friends)
                    if shared_friends:
                        mutual_counts[friend_id] = len(shared_friends)

    max_heap = []
    for candidate_id, count in mutual_counts.items():
        heapq.heappush(max_heap, (-count, candidate_id))
    
    recommendations = []
    while max_heap:
        neg_count, candidate_id = heapq.heappop(max_heap)
        recommendations.append((candidate_id, -neg_count))
        
    return recommendations


# ================= STEP 6 (INTERACTIVE CLI) =================
if __name__ == "__main__":
    graph = SocialGraph()
    history = ActionHistory()

    raw_profiles = [
        User(5, "Eve"),
        User(2, "Bob"),
        User(1, "Alice"),
        User(4, "David"),
        User(3, "Charlie")
    ]

    sorted_profiles = quicksort_users(raw_profiles)
    for user_profile in sorted_profiles:
        graph.add_user(user_profile)

    graph.add_friendship(1, 2)  # Alice <-> Bob
    graph.add_friendship(1, 3)  # Alice <-> Charlie
    graph.add_friendship(2, 4)  # Bob <-> David
    graph.add_friendship(2, 5)  # Bob <-> Eve
    graph.add_friendship(3, 4)  # Charlie <-> David
    graph.add_friendship(4, 5)  # David <-> Eve

    current_user_id = 1 

    while True:
        session_user = graph.network[current_user_id]
        print("\n" + "="*50)
        print(f"   SOCIAL NETWORK INTERACTIVE PORTAL | USER: {session_user.name.upper()} (ID: {current_user_id})")
        print("="*50)
        print("1. View My Profile & Direct Friends (Dashboard)")
        print("2. Get Intelligent Friend Recommendations (Heap + BFS)")
        print("3. Add a New Friend")
        print("4. Undo Last Action (LIFO Stack Rollback)")
        print("5. Switch Active User Profile")
        print("6. Exit Application")
        print("="*50)
        
        choice = input("Select an option (1-6): ").strip()

        if choice == "1":
            print("\n" + "═"*50)
            print(f" 👤  USER PROFILE CARD: {session_user.name.upper()} ")
            print("═"*50)
            print(f"  ▪️ Account ID     : {session_user.user_id}")
            print(f"  ▪️ Account Status : Active Student Network")
            print(f"  ▪️ Network Layer  : Connected Node")
            print("─"*50)
            
            if session_user.friends:
                print(f"  👥 DIRECT CONNECTIONS ({len(session_user.friends)})")
                print("─"*50)
                for f_id in session_user.friends:
                    friend_name = graph.network[f_id].name
                    print(f"   [ID: {f_id}] ➔ {friend_name:<12} | Status: Mutual Node")
            else:
                print("  👥 CONNECTIONS: No active friends linked to this profile.")
            print("═"*50)

        elif choice == "2":
            print(f"\n--- GENERATING RECOMMENDATIONS FOR {session_user.name.upper()} ---")
            recs = get_friend_recommendations(current_user_id, graph)
            if not recs:
                print("No recommendations available for this user profile right now.")
            else:
                for rank, (candidate_id, score) in enumerate(recs, start=1):
                    candidate_name = graph.network[candidate_id].name
                    print(f"Rank {rank}: {candidate_name} (Shared Mutual Connections: {score})")

        elif choice == "3":
            print(f"\n--- REGISTER NEW FRIEND CONNECTION ---")
            available_users = [u_id for u_id in graph.network if u_id != current_user_id and u_id not in session_user.friends]
            
            if not available_users:
                print("You are already connected with everyone in the network!")
                continue
                
            print("Available users to add:")
            for u_id in available_users:
                print(f" -> ID [{u_id}]: {graph.network[u_id].name}")
                
            try:
                target_id = int(input("\nEnter the ID of the user you want to add: "))
                if target_id in available_users:
                    graph.add_friendship(current_user_id, target_id)
                    history.log_action("ADD_FRIEND", (current_user_id, target_id))
                    print(f"[Success] You are now friends with {graph.network[target_id].name}!")
                else:
                    print("[Error] Invalid choice or user is already your friend.")
            except ValueError:
                print("[Error] Integer inputs only please.")

        elif choice == "4":
            history.undo(graph)

        elif choice == "5":
            print(f"\n--- SWITCH ACTIVE USER SESSION ---")
            for u_id, user_obj in graph.network.items():
                print(f" -> ID [{u_id}]: {user_obj.name}")
            try:
                new_id = int(input("\nEnter target profile ID: "))
                if new_id in graph.network:
                    current_user_id = new_id
                    print(f"Switched session owner to {graph.network[new_id].name}.")
                else:
                    print("[Error] Target profile ID does not exist.")
            except ValueError:
                print("[Error] Integer inputs only please.")

        elif choice == "6":
            print("\nShutting down social database network portal. Goodbye!")
            break
        else:
            print("[Error] Invalid selection option. Choose numbers between 1 and 6.")