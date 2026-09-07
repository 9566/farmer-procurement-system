"""
Important FAQ data for Smart Farmer Procurement
and Real-Time Queue Management System.

These answers are based on the project's uploaded
FAQ/viva document.
"""

FAQ_DATA = [

    # ============================================================
    # PROJECT BASICS
    # ============================================================

    {
        "id": 1,
        "question": "Aapne ye problem hi kyun choose ki?",
        "keywords": [
            "why choose problem",
            "why this problem",
            "problem choose",
            "why farmer problem",
            "problem kyun choose",
            "why selected this problem"
        ],
        "answer": (
            "We chose this problem because farmers can lose significant "
            "time at procurement centres due to unorganized queues and "
            "uncertain waiting times. Our solution focuses on making the "
            "procurement process more organized, transparent and convenient."
        )
    },

    {
        "id": 2,
        "question": "Aapke solution ka main objective kya hai?",
        "keywords": [
            "main objective",
            "objective",
            "purpose",
            "goal of project",
            "project objective",
            "main goal"
        ],
        "answer": (
            "Our main objective is to reduce unnecessary waiting and "
            "overcrowding at procurement centres by combining slot booking, "
            "digital tokens and real-time queue management."
        )
    },

    {
        "id": 3,
        "question": "Aapka solution existing system se better kaise hai?",
        "keywords": [
            "better than existing",
            "existing system",
            "existing process",
            "advantage",
            "why better",
            "improvement"
        ],
        "answer": (
            "Existing processes may involve manual queues and limited "
            "visibility for farmers. Our platform gives farmers a digital "
            "token, live queue status and estimated waiting time, while "
            "officers get a centralized dashboard to manage the queue."
        )
    },

    {
        "id": 4,
        "question": "Aapki innovation kya hai?",
        "keywords": [
            "innovation",
            "innovative",
            "what is innovation",
            "special feature",
            "unique"
        ],
        "answer": (
            "The innovation is the integration of the complete procurement "
            "journey in one platform—from slot booking and queue management "
            "to procurement and payment tracking."
        )
    },

    {
        "id": 5,
        "question": "Farmer ko isse actual benefit kya milega?",
        "keywords": [
            "farmer benefit",
            "benefit to farmer",
            "farmer advantage",
            "benefit",
            "how farmer benefits"
        ],
        "answer": (
            "The farmer can book a slot, receive a token, know their queue "
            "position and estimated waiting time, and track procurement and "
            "payment status without repeatedly visiting or waiting at the centre."
        )
    },

    {
        "id": 6,
        "question": "Agar 1 lakh farmers use karein toh?",
        "keywords": [
            "1 lakh farmers",
            "100000 farmers",
            "large users",
            "many users",
            "scalability"
        ],
        "answer": (
            "We are using a cloud-based architecture, which can be scaled "
            "according to demand. For large-scale deployment, database "
            "optimization, load management and appropriate cloud resources "
            "can support a much larger number of users."
        )
    },

    {
        "id": 7,
        "question": "Ek hi time par 1000 farmers same slot book karein toh?",
        "keywords": [
            "1000 farmers",
            "same slot",
            "slot capacity",
            "capacity",
            "too many bookings"
        ],
        "answer": (
            "The system can enforce a maximum capacity for each slot. Once "
            "the capacity is reached, that slot becomes unavailable and the "
            "farmer is shown alternative slots."
        )
    },

    {
        "id": 8,
        "question": "Do farmers ko same token mil gaya toh?",
        "keywords": [
            "duplicate token",
            "same token",
            "two farmers same token",
            "token duplicate"
        ],
        "answer": (
            "Token generation should be handled using a transactional "
            "database operation rather than random generation. The system "
            "will maintain a separate token counter for each procurement "
            "centre and date."
        )
    },

    # ============================================================
    # FARMER / USABILITY
    # ============================================================

    {
        "id": 9,
        "question": "Farmer slot book karke aaya hi nahi toh?",
        "keywords": [
            "farmer absent",
            "no show",
            "did not come",
            "missed slot",
            "farmer not come"
        ],
        "answer": (
            "We can introduce a check-in mechanism at the procurement "
            "centre. If a farmer does not check in within the allowed time, "
            "the slot can be marked as missed and the queue can automatically "
            "move forward."
        )
    },

    {
        "id": 10,
        "question": "Farmer late ho gaya toh?",
        "keywords": [
            "farmer late",
            "late farmer",
            "late for slot",
            "grace period"
        ],
        "answer": (
            "A grace period can be provided. After that, the farmer can be "
            "moved to a later available slot instead of disturbing the current queue."
        )
    },

    {
        "id": 11,
        "question": "Gaon mein internet nahi hai toh?",
        "keywords": [
            "no internet",
            "village internet",
            "poor network",
            "low connectivity",
            "network problem"
        ],
        "answer": (
            "The website is designed to be lightweight and mobile-friendly. "
            "For low-connectivity areas, we can additionally support SMS "
            "notifications and assisted booking through the procurement centre."
        )
    },

    {
        "id": 12,
        "question": "Agar farmer ke paas smartphone hi nahi hai?",
        "keywords": [
            "no smartphone",
            "without smartphone",
            "farmer phone",
            "no mobile"
        ],
        "answer": (
            "The farmer can get assistance from the procurement centre or "
            "an authorized operator for booking. Important updates can also "
            "be provided through SMS."
        )
    },

    {
        "id": 13,
        "question": "Farmer ko English nahi aati toh?",
        "keywords": [
            "english",
            "regional language",
            "hindi",
            "language support",
            "multilingual"
        ],
        "answer": (
            "The interface can support regional languages and simple icons. "
            "Since the target users are farmers, multilingual support is an "
            "important part of our future deployment."
        )
    },

    {
        "id": 14,
        "question": "Agar farmer galat information bhar de?",
        "keywords": [
            "wrong information",
            "wrong details",
            "incorrect information",
            "wrong data",
            "validation"
        ],
        "answer": (
            "We can use input validation and verification against authorized "
            "farmer records. Important fields can also be verified before "
            "confirming the booking."
        )
    },

    # ============================================================
    # SECURITY
    # ============================================================

    {
        "id": 15,
        "question": "Aapka data secure kaise hai?",
        "keywords": [
            "data security",
            "secure data",
            "data safe",
            "security",
            "how secure"
        ],
        "answer": (
            "We use authenticated access and role-based permissions. "
            "Farmers should only access their own information, while "
            "administrative data should be accessible only to authorized officers."
        )
    },

    {
        "id": 16,
        "question": "Hacker ne farmer ka account access kar liya toh?",
        "keywords": [
            "hacker",
            "account hacked",
            "hack account",
            "unauthorized access",
            "cyber security"
        ],
        "answer": (
            "We can strengthen authentication using OTP or multi-factor "
            "authentication, secure session management and strict database "
            "security rules. Suspicious activity can also be monitored."
        )
    },

    {
        "id": 17,
        "question": "Aap farmer ka kaunsa data store kar rahe ho?",
        "keywords": [
            "farmer data",
            "stored data",
            "what data",
            "personal data",
            "information stored"
        ],
        "answer": (
            "We only need information required for registration and "
            "procurement, such as farmer identification, contact details, "
            "booking details, crop and quantity. We should avoid collecting "
            "unnecessary personal information."
        )
    },

    {
        "id": 18,
        "question": "Aap password database mein store karoge?",
        "keywords": [
            "password database",
            "password storage",
            "plain text password",
            "password security"
        ],
        "answer": (
            "No. Passwords should not be stored as plain text. Authentication "
            "services should securely handle user credentials."
        )
    },

    # ============================================================
    # DATA / AI / ML
    # ============================================================

    {
        "id": 19,
        "question": "Dataset kahan se liya?",
        "keywords": [
            "dataset",
            "data source",
            "where dataset",
            "data taken",
            "source of data"
        ],
        "answer": (
            "Our current prototype uses simulated sample data for "
            "demonstration. For actual deployment, the system would use "
            "verified data provided by the authorized procurement department."
        )
    },

    {
        "id": 20,
        "question": "Aapke waiting-time prediction ka basis kya hai?",
        "keywords": [
            "waiting time prediction",
            "waiting prediction",
            "waiting time basis",
            "estimated waiting",
            "prediction basis"
        ],
        "answer": (
            "Currently, our prototype estimates waiting time using the "
            "number of farmers ahead in the queue and an average processing "
            "time. In future, this can be improved using historical centre-level data."
        )
    },

    {
        "id": 21,
        "question": "Isme AI/ML kahan hai?",
        "keywords": [
            "ai",
            "ml",
            "artificial intelligence",
            "machine learning",
            "where ai",
            "where ml"
        ],
        "answer": (
            "AI is not necessary for the core functionality. However, once "
            "sufficient historical data is available, machine learning can "
            "be used to predict waiting time, peak hours and expected procurement load."
        )
    },

    {
        "id": 22,
        "question": "Aapne ML model train kiya hai?",
        "keywords": [
            "ml model trained",
            "trained model",
            "machine learning model",
            "model train"
        ],
        "answer": (
            "Not in the current prototype. Our current focus is establishing "
            "the digital workflow and queue-management system. ML can be added "
            "after sufficient real historical data is collected."
        )
    },

    # ============================================================
    # REAL-TIME QUEUE
    # ============================================================

    {
        "id": 23,
        "question": "Real-time queue kaise update hoga?",
        "keywords": [
            "real time queue",
            "queue update",
            "live queue",
            "queue realtime",
            "queue update mechanism"
        ],
        "answer": (
            "The queue information is stored in the cloud database. When the "
            "officer updates the current token, connected farmer dashboards "
            "can receive the updated queue information in real time."
        )
    },

    {
        "id": 24,
        "question": "Agar server down ho gaya toh?",
        "keywords": [
            "server down",
            "server failure",
            "server problem",
            "system down"
        ],
        "answer": (
            "We would use cloud infrastructure with backup and monitoring "
            "mechanisms. For critical operations, the centre can also maintain "
            "a temporary manual fallback so procurement does not stop completely."
        )
    },

    {
        "id": 25,
        "question": "Aapka system scale kaise karega?",
        "keywords": [
            "scale system",
            "scalable",
            "scalability",
            "system scale",
            "new centres"
        ],
        "answer": (
            "The system can use a centre-based architecture where each "
            "procurement centre has its own slots, queue and bookings. "
            "New centres can be added without changing the overall architecture."
        )
    },

    # ============================================================
    # GOVERNMENT / PAYMENT
    # ============================================================

    {
        "id": 26,
        "question": "Government ke existing systems ke saath integrate kaise karoge?",
        "keywords": [
            "government integration",
            "government system",
            "existing government",
            "api integration",
            "govt database"
        ],
        "answer": (
            "We would expose secure APIs or use approved integration "
            "mechanisms provided by the concerned department. We would not "
            "directly access government databases without authorization."
        )
    },

    {
        "id": 27,
        "question": "Payment actually kaise hoga?",
        "keywords": [
            "payment",
            "payment process",
            "actual payment",
            "farmer payment",
            "payment integration"
        ],
        "answer": (
            "Our prototype only demonstrates payment status tracking. In "
            "real deployment, payment information would be integrated with "
            "the authorized government payment or procurement system rather "
            "than handling the farmer's money ourselves."
        )
    },

    {
        "id": 28,
        "question": "SMS kaise bhejoge?",
        "keywords": [
            "sms",
            "sms notification",
            "send sms",
            "message farmer",
            "notifications"
        ],
        "answer": (
            "For the prototype we can demonstrate notifications within the "
            "application. In real deployment, an authorized SMS gateway can "
            "be integrated to send booking, queue and payment updates."
        )
    },

    {
        "id": 29,
        "question": "Agar farmer booking cancel karna chahe?",
        "keywords": [
            "cancel booking",
            "booking cancellation",
            "cancel slot",
            "cancellation"
        ],
        "answer": (
            "The farmer can be given a cancellation option before a defined "
            "cut-off time. The released slot can then be made available to another farmer."
        )
    },

    {
        "id": 30,
        "question": "Agar procurement centre ki capacity khatam ho gayi?",
        "keywords": [
            "centre capacity",
            "capacity full",
            "procurement centre full",
            "slot full",
            "capacity reached"
        ],
        "answer": (
            "The system will stop accepting bookings once the centre or slot "
            "reaches its configured capacity and will suggest another "
            "available slot or nearby centre."
        )
    },

    # ============================================================
    # TOKEN / QUEUE LOGIC
    # ============================================================

    {
        "id": 31,
        "question": "Token kaise decide hoga?",
        "keywords": [
            "token decide",
            "token generation",
            "token number",
            "how token",
            "token sequence"
        ],
        "answer": (
            "Tokens will be generated sequentially based on the selected "
            "procurement centre, date and slot. Each centre and date can "
            "maintain its own token sequence."
        )
    },

    {
        "id": 32,
        "question": "Token 47 wale ko token 48 se pehle bula diya toh?",
        "keywords": [
            "token sequence",
            "47 before 48",
            "token order",
            "queue sequence",
            "priority token"
        ],
        "answer": (
            "The officer dashboard controls the queue, but the system "
            "maintains the sequence. Any exception such as priority or "
            "missed booking should be recorded so that the queue remains transparent."
        )
    },

    {
        "id": 33,
        "question": "VIP ya priority farmer aa gaya toh?",
        "keywords": [
            "vip farmer",
            "priority farmer",
            "priority category",
            "special farmer"
        ],
        "answer": (
            "If government policy allows priority categories, the system can "
            "support configurable priority rules. Such changes should be "
            "authorized and recorded to maintain transparency."
        )
    },

    {
        "id": 34,
        "question": "Agar do procurement centres hain toh token same ho sakta hai?",
        "keywords": [
            "two centres",
            "same token centres",
            "same token different centre",
            "token centre"
        ],
        "answer": (
            "Yes, the same token number can exist at different centres because "
            "the queue is maintained separately for each centre and date."
        )
    },

    {
        "id": 35,
        "question": "Queue mein kitne farmers hain kaise pata chalega?",
        "keywords": [
            "queue count",
            "farmers in queue",
            "queue position",
            "number of farmers",
            "queue length"
        ],
        "answer": (
            "The system calculates the number of active bookings for that "
            "centre and date and compares them with the currently served token."
        )
    },

    {
        "id": 36,
        "question": "Estimated waiting time galat hua toh?",
        "keywords": [
            "waiting time wrong",
            "wrong estimate",
            "estimated waiting wrong",
            "prediction error"
        ],
        "answer": (
            "Initially, it is an estimate based on queue position and average "
            "processing time. As real historical data becomes available, the "
            "prediction can be improved using actual processing times and "
            "centre-specific patterns."
        )
    },

    # ============================================================
    # PROJECT ARCHITECTURE
    # ============================================================

    {
        "id": 37,
        "question": "Frontend aur backend kya hai?",
        "keywords": [
            "frontend",
            "backend",
            "frontend backend",
            "technology frontend",
            "technology backend"
        ],
        "answer": (
            "The frontend uses HTML, CSS and JavaScript. The recommended "
            "project backend architecture uses Python with FastAPI, with "
            "MySQL and SQLAlchemy for database management."
        )
    },

    {
        "id": 38,
        "question": "Firebase kyun, SQL database kyun nahi?",
        "keywords": [
            "firebase vs sql",
            "firebase sql",
            "why firebase",
            "why sql",
            "database choice"
        ],
        "answer": (
            "For a prototype, Firebase can provide faster development and "
            "real-time updates with less backend infrastructure. For the "
            "planned project architecture, MySQL with SQLAlchemy is recommended "
            "for structured procurement data and database management."
        )
    },

    {
        "id": 39,
        "question": "Aapne backend mein kya banaya?",
        "keywords": [
            "backend work",
            "backend built",
            "what backend",
            "backend features",
            "backend development"
        ],
        "answer": (
            "The backend is responsible for APIs, authentication, database "
            "operations, booking management, queue management, procurement "
            "and payment status. The recommended implementation uses Python "
            "and FastAPI."
        )
    },

    # ============================================================
    # FUTURE / DEPLOYMENT
    # ============================================================

    {
        "id": 40,
        "question": "Future mein kya add karoge?",
        "keywords": [
            "future scope",
            "future features",
            "future",
            "what add future",
            "future development"
        ],
        "answer": (
            "Future improvements can include multilingual support, SMS "
            "notifications, government-system integration, advanced "
            "waiting-time prediction, analytics dashboards and assisted "
            "booking for low-connectivity areas."
        )
    },

    {
        "id": 41,
        "question": "AI ka future use kya hai?",
        "keywords": [
            "future ai",
            "ai future",
            "future machine learning",
            "ai prediction"
        ],
        "answer": (
            "With sufficient historical data, AI can predict peak hours, "
            "expected waiting time and procurement workload, helping centres "
            "plan their resources better."
        )
    },

    {
        "id": 42,
        "question": "GPS/location use karoge?",
        "keywords": [
            "gps",
            "location",
            "nearby centre",
            "location feature",
            "maps"
        ],
        "answer": (
            "Location can be used to show nearby procurement centres and help "
            "farmers choose a convenient centre, subject to the department's "
            "eligibility and allocation rules."
        )
    },

    {
        "id": 43,
        "question": "Mobile app banaoge ya website?",
        "keywords": [
            "mobile app",
            "website",
            "android app",
            "web platform",
            "app or website"
        ],
        "answer": (
            "We started with a responsive web platform because it is easier "
            "to access across devices. A dedicated Android application can "
            "be developed later if user adoption justifies it."
        )
    },

    {
        "id": 44,
        "question": "Aapki biggest limitation kya hai?",
        "keywords": [
            "limitation",
            "biggest limitation",
            "disadvantage",
            "project limitation"
        ],
        "answer": (
            "Our current prototype uses simulated data and does not yet "
            "integrate with actual government procurement databases or SMS "
            "infrastructure. These would be addressed during pilot deployment "
            "with the concerned department."
        )
    },

    {
        "id": 45,
        "question": "Government mein actual implementation kaise hoga?",
        "keywords": [
            "government implementation",
            "actual implementation",
            "deploy government",
            "implementation"
        ],
        "answer": (
            "We would start with a pilot at selected procurement centres, "
            "integrate with authorized government systems, train centre staff, "
            "collect feedback and measure results before scaling."
        )
    },

    {
        "id": 46,
        "question": "Project ka one-line USP kya hai?",
        "keywords": [
            "usp",
            "one line usp",
            "unique selling point",
            "project special"
        ],
        "answer": (
            "We convert an unpredictable waiting process into a planned, "
            "trackable and transparent procurement journey for every farmer."
        )
    },

    # ============================================================
    # GENERAL IMPORTANT QUESTIONS
    # ============================================================

    {
        "id": 47,
        "question": "Government ka actual benefit kya hai?",
        "keywords": [
            "government benefit",
            "govt benefit",
            "government advantage",
            "benefit government"
        ],
        "answer": (
            "It can improve operational efficiency, reduce overcrowding, "
            "provide better monitoring and create digital records that can "
            "support decision-making."
        )
    },

    {
        "id": 48,
        "question": "Is project ka ROI kya hai?",
        "keywords": [
            "roi",
            "return on investment",
            "project roi",
            "investment"
        ],
        "answer": (
            "ROI can be evaluated through measurable improvements such as "
            "reduced average waiting time, reduced congestion, lower manual "
            "workload and improved processing efficiency."
        )
    },

    {
        "id": 49,
        "question": "Farmer ko kaise pata chalega ki uska number aa gaya?",
        "keywords": [
            "number came",
            "turn came",
            "notification",
            "token called",
            "farmer notification"
        ],
        "answer": (
            "The farmer can receive an in-app notification, and in the "
            "production version, SMS alerts can be sent when the farmer's "
            "turn is approaching."
        )
    },

    {
        "id": 50,
        "question": "Multiple states mein alag-alag rules hain toh?",
        "keywords": [
            "multiple states",
            "different rules",
            "state rules",
            "different state",
            "configurable rules"
        ],
        "answer": (
            "The system can use configurable rules for slot capacity, "
            "procurement timings and eligibility so that different centres "
            "can follow their applicable policies."
        )
    }
]