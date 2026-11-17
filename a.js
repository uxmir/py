const express = require("express");
const fs = require("fs");
const app = express();

app.use(express.json());

// গ্লোবাল অ্যারে যা সময়ের সাথে সাথে মেমোরি লিক ঘটাবে
const requestLogs = [];
const users = [
  { id: 1, name: "Rahim", role: "user", balance: 500 },
  { id: 2, name: "Karim", role: "admin", balance: 1500 },
];

// --- ১. PROTOTYPE POLLUTION & UNSAFE MERGE ---
function mergeObjects(target, source) {
  for (let key in source) {
    // ইস্যু ১: __proto__ বা constructor চেক না করায় Prototype Pollution অ্যাটাক হতে পারে
    if (typeof source[key] === "object" && source[key] !== null) {
      if (!target[key]) target[key] = {};
      mergeObjects(target[key], source[key]);
    } else {
      target[key] = source[key];
    }
  }
  return target;
}

app.post("/update-settings", (req, res) => {
  const defaultSettings = { theme: "light", notifications: true };
  const updated = mergeObjects(defaultSettings, req.body);
  res.json({ settings: updated });
});

// --- ২. ASYNC / AWAIT FOR-EACH TRAP & UNHANDLED PROMISE ---
app.post("/process-payouts", async (req, res) => {
  const { userIds, bonus } = req.body;

  // ইস্যু ২: Array.forEach এর ভেতর async/await কাজ করে না, ফলে রেসপন্স আগেই চলে যাবে
  userIds.forEach(async (id) => {
    const user = users.find((u) => u.id == id); // ইস্যু ৩: == (Loose equality) ব্যবহার করা হয়েছে
    if (user) {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      user.balance += bonus; // ইস্যু ৪: bonus স্ট্রিং হলে ("100") ব্যালেন্স কনক্যাট হয়ে যাবে (500 + "100" = "500100")
    }
  });

  // লুপ শেষ হওয়ার আগেই রেসপন্স পাঠিয়ে দিচ্ছে!
  res.json({ message: "Payouts completed!", users });
});

// --- ৩. EVENT LOOP BLOCKING & SYNC FILE I/O ---
app.get("/heavy-logs", (req, res) => {
  // ইস্যু ৫: বড় ফাইল সিঙ্ক্রোনাসভাবে রিড করলে Node.js এর মেইন থ্রেড / ইভেন্ট লুপ ব্লক হয়ে যাবে
  const data = fs.readFileSync("./huge_server_logs.txt", "utf8");

  // ইস্যু ৬: ইনফিনিট বা হেভি সিঙ্ক্রোনাস লুপ যা সার্ভার হ্যাং করে দেবে
  let count = 0;
  for (let i = 0; i < 1e10; i++) {
    count += i;
  }

  requestLogs.push({ time: Date.now(), data }); // ইস্যু ৭: আনলিমিটেড পুশ করার কারণে Memory Leak
  res.send({ count, length: data.length });
});

// --- ৪. REGEX DENIAL OF SERVICE (ReDoS) & EVAL ---
app.post("/calculate", (req, res) => {
  const { expression, email } = req.body;

  // ইস্যু ৮: Catastrophic Backtracking যুক্ত দুর্বল Regex (ReDoS অ্যাটাকের ঝুঁকি)
  const emailRegex = /^([a-zA-Z0-9]+)+@([a-zA-Z0-9]+)+\.[a-zA-Z]{2,}$/;
  if (!emailRegex.test(email)) {
    return res.status(400).json({ error: "Invalid email" });
  }

  // ইস্যু ৯: ইউজারের ইনপুটে সরাসরি eval() ব্যবহার (Remote Code Execution - RCE)
  const result = eval(expression);
  res.json({ result });
});

const jwt = require("jsonwebtoken");

// ইস্যু ১: হার্ডকোডেড সিক্রেট কী
const JWT_SECRET = "my_secret_123";

// ১. টোকেন ভেরিফিকেশন ফাংশন
function verifyUserToken(token) {
  // ইস্যু ২: jwt.decode() সিগনেচার ভেরিফাই না করেই পেলোড রিটার্ন করে (jwt.verify() ব্যবহার করা উচিত)
  const decoded = jwt.decode(token);
  
  if (!decoded) {
    return null;
  }
  return decoded;
}

// ২. শপিং কার্টের ডিসকাউন্ট ও টোটাল ক্যালকুলেশন
function calculateCartTotal(cartItems, discountPercent) {
  let total = 0;

  // ইস্যু ৩: var ব্যবহার এবং অ্যাসিঙ্ক বা ক্লোজার বাগের ঝুঁকি, সাথে প্যারামিটার ভ্যালিডেশন নেই
  for (var i = 0; i <= cartItems.length; i++) { 
    // ইস্যু ৪: i <= cartItems.length দেওয়ায় শেষ ইটারেশনে cartItems[i] undefined হবে এবং TypeError দিবে
    total += cartItems[i].price * cartItems[i].qty;
  }

  // ইস্যু ৫: ফ্লোটিং পয়েন্ট প্রিসিশন বাগ (যেমন: 0.1 + 0.2 = 0.30000000000000004) এবং নেগেটিভ ডিসকাউন্ট চেক নেই
  const finalAmount = total - (total * discountPercent) / 100;

  return finalAmount;
}

module.exports = { verifyUserToken, calculateCartTotal };

app.listen(3000, () => console.log("Server running on port 3000"));