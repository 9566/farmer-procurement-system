// =====================================================================
// >>> CHANGE THIS if your backend runs somewhere else <<<
// Local development default matches `uvicorn main:app --reload`.
// After deployment, set this to your deployed backend URL, e.g.
// "https://your-app.onrender.com"
// =====================================================================
const API_BASE_URL = "https://farmer-procurement-system.onrender.com";
const WS_BASE_URL = "wss://farmer-procurement-system.onrender.com";

// Farmer auth header (token saved by login.html)
function authHeaders() {
    const token = localStorage.getItem("access_token");
    return token ? { "Authorization": "Bearer " + token } : {};
}

// -----------------------------------------------------------------
// ESCAPE HTML
// Every page injects backend/user-supplied text (names, mobiles,
// centre names, payment method/transaction id, error messages) into
// innerHTML. Without escaping, any of those fields can carry a script
// payload — most seriously: an operator's free-text "payment method"
// or "transaction id" (entered in procurement.html) is later rendered
// unescaped for the farmer in payment.html. Wrap ANY value that did
// not originate as a hardcoded string in this app with escapeHtml()
// before putting it in innerHTML.
// -----------------------------------------------------------------

function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, (ch) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
    }[ch]));
}

// -----------------------------------------------------------------
// TOAST NOTIFICATIONS
// Small, temporary confirmations ("Booking confirmed", "Logged out")
// layered on top of the inline <div id="msgBox"> messages each page
// already uses for form-level errors.
// -----------------------------------------------------------------

function ensureToastStack() {
    let stack = document.getElementById("toast-stack");
    if (!stack) {
        stack = document.createElement("div");
        stack.id = "toast-stack";
        document.body.appendChild(stack);
    }
    return stack;
}

function showToast(message, type = "info", duration = 3200) {
    const stack = ensureToastStack();
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message; // textContent is safe as-is, no escaping needed
    stack.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transition = "opacity 0.2s ease";
        setTimeout(() => toast.remove(), 200);
    }, duration);
}

// -----------------------------------------------------------------
// BUTTON LOADING STATE
// Disables a button, swaps its label for a spinner + text, and
// restores it afterward. Prevents double-submits on slow networks.
// -----------------------------------------------------------------

function setButtonLoading(button, isLoading, loadingText = "Please wait…") {
    if (!button) return;
    if (isLoading) {
        button.dataset.originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = `<span class="spinner"></span> ${escapeHtml(loadingText)}`;
    } else {
        button.disabled = false;
        if (button.dataset.originalText) {
            button.innerHTML = button.dataset.originalText;
        }
    }
}

// -----------------------------------------------------------------
// THEME TOGGLE
// Injected into every navbar automatically so each page doesn't need
// to repeat the same markup. Preference persists in localStorage.
// -----------------------------------------------------------------

function initTheme() {
    const saved = localStorage.getItem("theme");
    if (saved === "dark") document.body.classList.add("dark");

    const navLinks = document.querySelector(".navbar .nav-links");
    if (!navLinks || document.querySelector(".theme-toggle")) return;

    const btn = document.createElement("button");
    btn.className = "theme-toggle";
    btn.type = "button";
    btn.title = "Toggle light / dark theme";
    btn.textContent = document.body.classList.contains("dark") ? "☀" : "☾";

    btn.addEventListener("click", () => {
        document.body.classList.toggle("dark");
        const isDark = document.body.classList.contains("dark");
        localStorage.setItem("theme", isDark ? "dark" : "light");
        btn.textContent = isDark ? "☀" : "☾";
    });

    navLinks.appendChild(btn);
}

document.addEventListener("DOMContentLoaded", initTheme);

// -----------------------------------------------------------------
// SIMPLE FETCH HELPER
// Wraps fetch + JSON parsing + a friendly message when the backend
// is unreachable, since that's the single most common failure mode
// during local development ("is uvicorn running?").
// -----------------------------------------------------------------

async function apiRequest(path, options = {}) {
    try {
        const res = await fetch(`${API_BASE_URL}${path}`, options);
        let body = null;
        try { body = await res.json(); } catch (_) { /* empty body */ }
        return { ok: res.ok, status: res.status, body };
    } catch (err) {
        console.error("Network error calling", path, err);
        return {
            ok: false,
            status: 0,
            body: { detail: `Could not reach the server at ${API_BASE_URL}. Is the backend running?` },
        };
    }
}

// -----------------------------------------------------------------
// VISUAL LAYER (additive only — nothing above this line changed)
//
// These three helpers are purely decorative and never touch backend
// logic, localStorage keys, or element IDs the pages rely on. They
// are called once from DOMContentLoaded below, alongside initTheme().
// -----------------------------------------------------------------

// 3D tilt for the hero token ticket. Deliberately scoped to a single
// element per page (".tilt-card") rather than every card, per the
// "one orchestrated moment" principle — hover tilts elsewhere in the
// app would be noise, not signal.
function initTiltCards() {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    if (window.matchMedia("(pointer: coarse)").matches) return; // skip on touch

    document.querySelectorAll(".tilt-card").forEach((card) => {
        const strength = 10;
        card.addEventListener("mousemove", (e) => {
            const rect = card.getBoundingClientRect();
            const px = (e.clientX - rect.left) / rect.width - 0.5;
            const py = (e.clientY - rect.top) / rect.height - 0.5;
            card.style.transform = `rotateY(${(-14 + px * strength * 2).toFixed(2)}deg) rotateX(${(6 - py * strength).toFixed(2)}deg)`;
        });
        card.addEventListener("mouseleave", () => {
            card.style.transform = "";
        });
    });
}

// Count-up animation for hero stat numbers, triggered once when they
// scroll into view — the single "reveal moment" for the homepage,
// rather than fade-ins scattered across every section.
function initCountUp() {
    const nodes = document.querySelectorAll("[data-count-to]");
    if (nodes.length === 0) return;

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        nodes.forEach((el) => { el.textContent = el.dataset.countTo; });
        return;
    }

    const animate = (el) => {
        const target = parseInt(el.dataset.countTo, 10) || 0;
        const suffix = el.dataset.countSuffix || "";
        const duration = 900;
        const start = performance.now();
        function tick(now) {
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.round(eased * target) + suffix;
            if (progress < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
    };

    if ("IntersectionObserver" in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    animate(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.4 });
        nodes.forEach((el) => observer.observe(el));
    } else {
        nodes.forEach(animate);
    }
}

document.addEventListener("DOMContentLoaded", initTiltCards);
document.addEventListener("DOMContentLoaded", initCountUp);

// -----------------------------------------------------------------
// BILINGUAL UI — English / Hindi
// Additive layer. Existing API, authentication, booking, queue,
// procurement, payment, dashboard, theme and visual features remain unchanged.
// The selected language is saved in localStorage and applies across all pages.
// -----------------------------------------------------------------
const UI_TRANSLATIONS = {
  "Language":"भाषा", "English":"English", "Hindi":"हिन्दी", "हिन्दी":"हिन्दी",
  "Farmer":"किसान", "Operator":"ऑपरेटर", "Admin":"व्यवस्थापक", "Home":"होम", "Login":"लॉगिन", "Logout":"लॉगआउट", "Dashboard":"डैशबोर्ड",
  "Register":"पंजीकरण", "New booking":"नई बुकिंग", "Live queue":"लाइव कतार", "Payment":"भुगतान", "Farmer login":"किसान लॉगिन", "Register as a farmer":"किसान के रूप में पंजीकरण करें", "Operator login":"ऑपरेटर लॉगिन", "Admin login":"व्यवस्थापक लॉगिन",
  "Create your account":"अपना खाता बनाएं", "Create an account":"खाता बनाएं", "Book a procurement slot":"खरीद स्लॉट बुक करें", "Check payment status":"भुगतान की स्थिति देखें", "Live queue status":"लाइव कतार की स्थिति", "Overview":"सारांश", "Welcome,":"स्वागत है,",
  "Your bookings":"आपकी बुकिंग", "Refresh":"रिफ्रेश", "Back to home":"होम पर वापस जाएं", "Back to dashboard":"डैशबोर्ड पर वापस जाएं", "Mobile number":"मोबाइल नंबर", "Password":"पासवर्ड", "Full name":"पूरा नाम", "Email (optional)":"ईमेल (वैकल्पिक)", "Village":"गांव", "District":"जिला", "State":"राज्य", "Role":"भूमिका",
  "Procurement centre":"खरीद केंद्र", "Procurement centre ID":"खरीद केंद्र आईडी", "Crop":"फसल", "Quantity (in the crop's unit)":"मात्रा (फसल की इकाई में)", "Date":"तारीख", "Time slot":"समय स्लॉट", "Confirm booking":"बुकिंग की पुष्टि करें", "Create account":"खाता बनाएं", "Log in":"लॉगिन करें",
  "Check status":"स्थिति देखें", "Show":"दिखाएं", "Hide":"छिपाएं", "Select a procurement centre":"खरीद केंद्र चुनें", "Select a crop":"फसल चुनें", "Your booking":"आपकी बुकिंग", "Booking ID":"बुकिंग आईडी", "Actual quantity":"वास्तविक मात्रा", "Quality status":"गुणवत्ता स्थिति", "Procurement status":"खरीद स्थिति",
  "Update procurement":"खरीद अपडेट करें", "Complete payment":"भुगतान पूरा करें", "Payment method":"भुगतान का तरीका", "Transaction ID (optional)":"लेन-देन आईडी (वैकल्पिक)", "Mark payment complete":"भुगतान पूरा हुआ चिह्नित करें", "Queue":"कतार", "Call next farmer":"अगले किसान को बुलाएं", "Refresh queue":"कतार रिफ्रेश करें", "Currently serving":"अभी सेवा में", "Waiting tokens":"प्रतीक्षा टोकन", "Connecting to live updates…":"लाइव अपडेट से जुड़ रहा है…",
  "Crop-wise procurement":"फसल के अनुसार खरीद", "Add a staff account":"स्टाफ खाता जोड़ें", "Create an admin or operator login directly — no need to run a script.":"व्यवस्थापक या ऑपरेटर लॉगिन सीधे बनाएं — स्क्रिप्ट चलाने की जरूरत नहीं है।", "Create staff account":"स्टाफ खाता बनाएं", "Payments completed":"पूर्ण भुगतान", "Total farmers":"कुल किसान", "Today's bookings":"आज की बुकिंग", "Active centres":"सक्रिय केंद्र", "Waiting farmers":"प्रतीक्षा कर रहे किसान", "Total procured qty":"कुल खरीदी मात्रा", "Total quantity procured":"कुल खरीदी मात्रा",
  "Administration":"प्रशासन", "For farmers":"किसानों के लिए", "For centres":"केंद्रों के लिए", "Track a queue":"कतार ट्रैक करें", "Payment status":"भुगतान स्थिति", "Admin dashboard":"व्यवस्थापक डैशबोर्ड", "A student BTech web development project":"बीटेक वेब डेवलपमेंट छात्र परियोजना",
  "Open before sunrise, every market day":"हर बाजार के दिन सूर्योदय से पहले खुला", "Sell your harvest without standing in the queue.":"कतार में खड़े हुए बिना अपनी फसल बेचें।", "How a booking becomes a payment":"बुकिंग से भुगतान तक का सफर", "Four steps, start to finish. Nothing skips ahead of the ledger.":"शुरू से अंत तक चार चरण। कोई भी चरण रिकॉर्ड से आगे नहीं जाता।", "Register once":"एक बार पंजीकरण करें", "Book a slot":"स्लॉट बुक करें", "Track your token":"अपना टोकन ट्रैक करें", "Get paid, on record":"रिकॉर्ड के साथ भुगतान पाएं", "Now serving":"अभी सेवा में", "Up next":"अगले नंबर", "This is what your token looks like once it's called.":"बुलाए जाने पर आपका टोकन ऐसा दिखाई देगा।",
  "You haven't booked a slot yet.":"आपने अभी तक कोई स्लॉट बुक नहीं किया है।", "Book your first slot":"अपना पहला स्लॉट बुक करें", "No bookings yet":"अभी कोई बुकिंग नहीं", "No centres available":"कोई केंद्र उपलब्ध नहीं", "No crops available":"कोई फसल उपलब्ध नहीं", "No one waiting.":"कोई प्रतीक्षा में नहीं है।", "Loading…":"लोड हो रहा है…", "Loading centres…":"केंद्र लोड हो रहे हैं…", "Loading crops…":"फसलें लोड हो रही हैं…", "Loading your bookings…":"आपकी बुकिंग लोड हो रही है…", "Connected — live updates active.":"कनेक्ट हो गया — लाइव अपडेट सक्रिय हैं।", "Connection error, retrying…":"कनेक्शन त्रुटि, फिर प्रयास किया जा रहा है…", "Disconnected. Reconnecting…":"डिस्कनेक्ट हो गया। फिर से कनेक्ट किया जा रहा है…",
  "Enter a procurement centre ID.":"खरीद केंद्र आईडी दर्ज करें।", "Enter a booking ID.":"बुकिंग आईडी दर्ज करें।", "Enter a valid actual quantity.":"मान्य वास्तविक मात्रा दर्ज करें।", "Please select a procurement centre and a crop.":"कृपया खरीद केंद्र और फसल चुनें।", "Select a booking first.":"पहले एक बुकिंग चुनें।", "Only works after procurement for this booking is COMPLETED.":"यह तभी काम करता है जब इस बुकिंग की खरीद COMPLETED हो।", "Marking a booking COMPLETED automatically calculates the payment (quantity × crop MSP).":"बुकिंग को COMPLETED करने पर भुगतान अपने आप निकाला जाता है (मात्रा × फसल MSP)।",
  "10 digits, no spaces or country code.":"10 अंक, बिना स्पेस या देश कोड के।", "At least 6 characters.":"कम से कम 6 अक्षर।", "Takes under a minute. You'll use your mobile number to log in.":"एक मिनट से कम समय लगेगा। लॉगिन के लिए आपका मोबाइल नंबर इस्तेमाल होगा।", "Use the mobile number you registered with.":"वही मोबाइल नंबर इस्तेमाल करें जिससे आपने पंजीकरण किया है।", "New here?":"यहां नए हैं?", "Lucknow Mandi Centre":"लखनऊ मंडी केंद्र",
  "Amount:":"राशि:", "Method:":"तरीका:", "Transaction ID:":"लेन-देन आईडी:", "Token":"टोकन", "Booking":"बुकिंग", "Qty":"मात्रा", "Cancel":"रद्द करें", "Status":"स्थिति", "GOOD":"अच्छी", "AVERAGE":"औसत", "REJECTED":"अस्वीकृत", "VERIFICATION":"सत्यापन", "WEIGHING":"तौल", "COMPLETED":"पूर्ण", "BOOKED":"बुक्ड", "PENDING":"लंबित", "WAITING":"प्रतीक्षा", "CALLED":"बुलाया गया", "PAYMENT_PENDING":"भुगतान लंबित", "PROCURED":"खरीद पूर्ण", "PAYMENT_COMPLETED":"भुगतान पूर्ण", "CANCELLED":"रद्द",
  "Checking credentials…":"जानकारी जांची जा रही है…", "Logging in…":"लॉगिन हो रहा है…", "Creating account…":"खाता बनाया जा रहा है…", "Booking…":"बुकिंग हो रही है…", "Checking…":"जांच हो रही है…", "Cancelling…":"रद्द किया जा रहा है…", "Calling…":"बुलाया जा रहा है…", "Updating…":"अपडेट हो रहा है…", "Completing…":"पूरा किया जा रहा है…", "Creating…":"बनाया जा रहा है…",
  "Logged out":"लॉगआउट हो गया", "Login successful":"लॉगिन सफल", "Admin login successful":"व्यवस्थापक लॉगिन सफल", "Welcome back!":"फिर से स्वागत है!", "Welcome to Smart Farmer Procurement!":"स्मार्ट किसान खरीद प्रणाली में आपका स्वागत है!", "Booking confirmed!":"बुकिंग की पुष्टि हो गई!", "Booking cancelled":"बुकिंग रद्द कर दी गई", "Payment completed":"भुगतान पूरा हो गया", "Procurement updated":"खरीद अपडेट हो गई", "Staff account created":"स्टाफ खाता बन गया", "Session expired, please log in again":"सत्र समाप्त हो गया, कृपया फिर से लॉगिन करें",
  "Could not load bookings.":"बुकिंग लोड नहीं हो सकीं।", "Could not load procurement centres. Check that the backend is running.":"खरीद केंद्र लोड नहीं हो सके। जांचें कि बैकएंड चल रहा है।", "Could not load crops. Check that the backend is running.":"फसलें लोड नहीं हो सकीं। जांचें कि बैकएंड चल रहा है।", "Booking failed":"बुकिंग विफल", "Login failed":"लॉगिन विफल", "Registration failed":"पंजीकरण विफल", "Invalid credentials":"जानकारी गलत है", "Invalid operator credentials":"ऑपरेटर की जानकारी गलत है", "Could not load dashboard":"डैशबोर्ड लोड नहीं हो सका", "Could not load crop analytics":"फसल विश्लेषण लोड नहीं हो सका", "Could not create staff account":"स्टाफ खाता नहीं बनाया जा सका", "Select a procurement centre for this operator.":"इस ऑपरेटर के लिए खरीद केंद्र चुनें।", "Could not call next farmer":"अगले किसान को नहीं बुलाया जा सका", "Procurement update failed":"खरीद अपडेट विफल", "Could not complete payment":"भुगतान पूरा नहीं किया जा सका", "No payment record found yet — procurement may not be completed.":"अभी भुगतान रिकॉर्ड नहीं मिला — संभव है खरीद पूरी नहीं हुई हो।", "Cancel this booking? This can't be undone.":"क्या इस बुकिंग को रद्द करें? इसे वापस नहीं किया जा सकता।",
  "Payment has been calculated — you can now mark it complete below.":"भुगतान की गणना हो गई है — अब आप नीचे इसे पूरा चिह्नित कर सकते हैं।", "Account created. Redirecting to login…":"खाता बन गया। लॉगिन पर भेजा जा रहा है…", "Mobile number must be exactly 10 digits.":"मोबाइल नंबर ठीक 10 अंकों का होना चाहिए।", "Track your queue":"अपनी कतार ट्रैक करें", "As an admin, you can act on any centre ID.":"व्यवस्थापक के रूप में आप किसी भी केंद्र आईडी पर काम कर सकते हैं।",
  "Smart Farmer Procurement":"स्मार्ट किसान खरीद", "Smart Farmer Procurement System":"स्मार्ट किसान खरीद प्रणाली", "Procurement Centre Operator":"खरीद केंद्र ऑपरेटर", "Admin Dashboard":"व्यवस्थापक डैशबोर्ड", "Book a Slot - Smart Farmer Procurement":"स्लॉट बुक करें - स्मार्ट किसान खरीद", "Dashboard - Smart Farmer Procurement":"डैशबोर्ड - स्मार्ट किसान खरीद", "Live Queue - Smart Farmer Procurement":"लाइव कतार - स्मार्ट किसान खरीद", "Payment - Smart Farmer Procurement":"भुगतान - स्मार्ट किसान खरीद", "Register - Smart Farmer Procurement":"पंजीकरण - स्मार्ट किसान खरीद", "Farmer Login - Smart Farmer Procurement":"किसान लॉगिन - स्मार्ट किसान खरीद", "Operator - Smart Farmer Procurement":"ऑपरेटर - स्मार्ट किसान खरीद", "Admin Dashboard - Smart Farmer Procurement":"व्यवस्थापक डैशबोर्ड - स्मार्ट किसान खरीद",
  "Built for market day — sunrise queues, verified crops, and payments you can see the moment they're cleared.":"बाजार के दिन के लिए बनाया गया — सुबह की कतारें, सत्यापित फसलें और भुगतान की जानकारी तुरंत।", "steps, booking to payment":"चरण, बुकिंग से भुगतान तक", "stages tracked per booking":"प्रति बुकिंग ट्रैक किए गए चरण", "queue position, updated as it moves":"कतार की स्थिति, आगे बढ़ते ही अपडेट", "Estimated payout at MSP:":"MSP पर अनुमानित भुगतान:", "Select a crop and quantity to see the estimated payout.":"अनुमानित भुगतान देखने के लिए फसल और मात्रा चुनें।", "final amount depends on the quantity verified at the centre":"अंतिम राशि केंद्र पर सत्यापित मात्रा पर निर्भर करेगी", "Could not reach the server at":"सर्वर तक पहुंच नहीं हो सकी:", "Is the backend running?":"क्या बैकएंड चल रहा है?", "You're assigned to centre":"आपको इस केंद्र के लिए नियुक्त किया गया है", "Procurement updated for booking":"बुकिंग की खरीद अपडेट हुई", "quantity":"मात्रा", "quality":"गुणवत्ता", "status":"स्थिति", "Created":"बनाया गया", "account for":"के लिए खाता", "mobile":"मोबाइल"
};

const UI_EXTRA_TRANSLATIONS = {
  "Book a slot at your nearest procurement centre, watch your token move up the line from your phone, and know the moment your payment clears — no more waiting at the gate to ask \"how much longer?\"":"अपने नजदीकी खरीद केंद्र पर स्लॉट बुक करें, फोन से अपना टोकन आगे बढ़ते देखें और भुगतान होते ही जानें — गेट पर खड़े होकर यह पूछने की जरूरत नहीं कि \"और कितना समय लगेगा?\"",
  "Add your name, mobile number and farm details. Takes about a minute.":"अपना नाम, मोबाइल नंबर और खेत की जानकारी जोड़ें। लगभग एक मिनट लगेगा।",
  "Choose a procurement centre, a crop, and a time that works for you.":"खरीद केंद्र, फसल और अपने लिए सुविधाजनक समय चुनें।",
  "Watch the live queue so you arrive right when you're needed — not before, not after.":"लाइव कतार देखें ताकि जरूरत के समय ही पहुंचें — न पहले, न बाद में।",
  "Once your crop is weighed and verified, your payment status updates the moment it's logged.":"फसल की तौल और सत्यापन के बाद, भुगतान दर्ज होते ही उसकी स्थिति अपडेट हो जाती है।",
  "Register, book a slot, and track your queue position and payment in real time.":"पंजीकरण करें, स्लॉट बुक करें और अपनी कतार की स्थिति व भुगतान को रीयल टाइम में ट्रैक करें।",
  "Call the next token, verify crop quality, and log procurement for your centre.":"अगला टोकन बुलाएं, फसल की गुणवत्ता सत्यापित करें और अपने केंद्र की खरीद दर्ज करें।",
  "Oversee every centre, manage staff accounts, and review procurement analytics.":"सभी केंद्रों की निगरानी करें, स्टाफ खाते प्रबंधित करें और खरीद विश्लेषण देखें।",
  "This account is registered as":"यह खाता इस भूमिका में पंजीकृत है",
  "not admin. Use the operator page instead.":"व्यवस्थापक नहीं है। इसके बजाय ऑपरेटर पेज का उपयोग करें।",
  "Could not load dashboard":"डैशबोर्ड लोड नहीं हो सका",
  "No centres yet — create one in the database first":"अभी कोई केंद्र नहीं है — पहले डेटाबेस में एक केंद्र बनाएं",
  "Payment of ₹":"भुगतान राशि ₹",
  "Amount:":"राशि:", "Method:":"तरीका:", "Transaction ID:":"लेन-देन आईडी:"
};

const UI_DYNAMIC_FRAGMENTS = [
  ["Booking #", "बुकिंग #"], ["Token ", "टोकन "], ["Qty ", "मात्रा "], ["Now serving token ", "अब सेवा में टोकन "],
  ["Payment of ₹", "भुगतान राशि ₹"], [" marked complete for booking #", " बुकिंग # के लिए पूर्ण चिह्नित"], ["Created ", "बनाया गया "],
  [" account for ", " के लिए खाता "], [" (mobile ", " (मोबाइल "], ["You're assigned to centre #", "आपको केंद्र # के लिए नियुक्त किया गया है"],
  ["Procurement updated for booking #", "बुकिंग # की खरीद अपडेट हुई"], [" — quantity ", " — मात्रा "], [", quality ", ", गुणवत्ता "], [", status ", ", स्थिति "],
  ["Estimated payout at MSP: ₹", "MSP पर अनुमानित भुगतान: ₹"], [" (final amount depends on the quantity verified at the centre).", " (अंतिम राशि केंद्र पर सत्यापित मात्रा पर निर्भर करेगी)।"],
  ["Payment of ₹", "भुगतान राशि ₹"]
];

function getLanguage() { return localStorage.getItem("language") === "hi" ? "hi" : "en"; }
function translateUI(value) {
  let text = String(value ?? "");
  if (getLanguage() !== "hi") return text;
  const allTranslations = Object.assign({}, UI_TRANSLATIONS, UI_EXTRA_TRANSLATIONS);
  Object.keys(allTranslations).sort((a,b) => b.length - a.length).forEach(key => {
    if (key && text.includes(key)) text = text.split(key).join(allTranslations[key]);
  });
  UI_DYNAMIC_FRAGMENTS.forEach(([from,to]) => { if (text.includes(from)) text = text.split(from).join(to); });
  return text;
}
function translatePage() {
  const hi = getLanguage() === "hi";
  document.documentElement.lang = hi ? "hi" : "en";
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) {
    const n = walker.currentNode;
    if (n.parentElement && !["SCRIPT","STYLE"].includes(n.parentElement.tagName)) nodes.push(n);
  }
  nodes.forEach(n => { const v = n.nodeValue; const t = translateUI(v); if (v !== t) n.nodeValue = t; });
  document.querySelectorAll("[placeholder],[title],[aria-label]").forEach(el => ["placeholder","title","aria-label"].forEach(a => { if (el.hasAttribute(a)) el.setAttribute(a, translateUI(el.getAttribute(a))); }));
  document.title = translateUI(document.title);
}
function initLanguageSwitcher() {
  const nav = document.querySelector(".navbar .nav-links");
  if (!nav || document.getElementById("languageSelectWrap")) return;
  const wrap = document.createElement("div");
  wrap.id = "languageSelectWrap";
  wrap.className = "language-switcher";
  wrap.innerHTML = '<span class="language-label">Language</span><select id="languageSelect" class="language-select" aria-label="Language"><option value="en">English</option><option value="hi">हिन्दी</option></select>';
  nav.appendChild(wrap);
  const select = document.getElementById("languageSelect");
  select.value = getLanguage();
  select.addEventListener("change", () => { localStorage.setItem("language", select.value); window.location.reload(); });
}

// Existing notifications, loading labels and confirmation dialogs also follow the selected language.
const _sfShowToast = window.showToast;
if (typeof _sfShowToast === "function") window.showToast = (message, type="info", duration=3200) => _sfShowToast(translateUI(message), type, duration);
const _sfSetButtonLoading = window.setButtonLoading;
if (typeof _sfSetButtonLoading === "function") window.setButtonLoading = (button,isLoading,loadingText="Please wait…") => _sfSetButtonLoading(button,isLoading,translateUI(loadingText));
const _sfConfirm = window.confirm;
window.confirm = message => _sfConfirm(translateUI(message));

document.addEventListener("DOMContentLoaded", () => {
  initLanguageSwitcher();
  translatePage();
  const observer = new MutationObserver(() => translatePage());
  observer.observe(document.body, { childList:true, subtree:true, characterData:true });
});
