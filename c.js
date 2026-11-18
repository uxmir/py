// test-sample.js

// ১. টাইপ কোয়ের্সন (Type Coercion) এবং লুজ ইকুয়ালিটি (Loose Equality)
const totalCount = "10";
if (totalCount == 10) {
  console.log("Equal values");
}

// ২. আনডিফাইন্ড ভ্যারিয়েবলের প্রপার্টি এক্সেস (Runtime Error)
const user = { name: "Rahim" };
console.log(user.address.city); 

// ৩. ভুল কনস্ট্যান্ট অ্যাসাইনমেন্ট (TypeError)
const API_URL = "https://api.example.com";
API_URL = "https://api.newsite.com"; 

// ৪. সিনট্যাক্স বা মিসিং ব্রাকেট (Syntax Error)
function calculateSum(a, b) {
  return a + b;
// } বন্ধ করা হয়নি