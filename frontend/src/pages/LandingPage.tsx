"use client";
import { motion } from "framer-motion";
import { Cog, Server, BarChart } from "lucide-react";

export default function LandingPage() {
  const scrollToFeatures = () => {
    const el = document.getElementById("features");
    el?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="relative w-screen bg-gradient-to-br from-blue-50 via-white to-blue-100 overflow-hidden rounded-xl">
      {/* Floating cloud shapes */}
      <div className="absolute top-10 left-20 w-40 h-20 bg-white rounded-full opacity-60 blur-2xl animate-pulse"></div>
      <div className="absolute top-40 left-1/3 w-60 h-32 bg-white rounded-full opacity-50 blur-3xl animate-pulse"></div>
      <div className="absolute bottom-20 right-40 w-48 h-24 bg-white rounded-full opacity-70 blur-2xl animate-pulse"></div>

      {/* Hero */}
      <div className="relative z-10 flex flex-col md:flex-row items-center justify-between max-w-7xl mx-auto px-6 py-20">
        {/* Left Section: Hero Content */}
        <div className="max-w-xl text-center md:text-left">
          <h1 className="text-5xl font-extrabold text-gray-900 leading-tight">
            CloudFlow <span className="text-blue-600">Platform</span>
          </h1>
          <p className="mt-6 text-lg text-gray-600">
            Build, scale, and deploy applications effortlessly in the cloud.
            With CloudFlow, experience seamless automation, secure workflows, and
            developer-friendly tools — all in one place.
          </p>

          <div className="mt-8">
            <button
              onClick={scrollToFeatures}
              className="px-6 py-3 rounded-2xl bg-blue-600 text-white font-semibold hover:bg-blue-700 shadow-lg transition"
            >
              Explore Features
            </button>
          </div>
        </div>

        {/* Right Section: Animated Connected Cogs */}
        <div className="relative mt-16 md:mt-0 md:w-1/2 flex items-center justify-center h-[300px]">
          {/* Cog 1 */}
          <motion.div
            initial={{ x: 200, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 1.5, delay: 0.5, ease: "easeOut" }}
            className="absolute"
          >
            <Cog size={160} className="text-blue-500 animate-spin-slow-reverse" />
          </motion.div>

          {/* Cog 2 */}
          <motion.div
            initial={{ x: 200, opacity: 0 }}
            animate={{ x: 70, y: 100, opacity: 1 }}
            transition={{ duration: 1.5, delay: 1, ease: "easeOut" }}
            className="absolute"
          >
            <Cog size={120} className="text-indigo-500 animate-spin-slow" />
          </motion.div>

          {/* Cog 3 */}
          <motion.div
            initial={{ x: 200, opacity: 0 }}
            animate={{ x: 120, y: -80, opacity: 1 }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            className="absolute"
          >
            <Cog size={180} className="text-purple-500 animate-spin-slow" />
          </motion.div>
        </div>
      </div>

      {/* Features Section */}
      <section id="features" className="relative z-10 bg-white w-full py-20">
        <div className="max-w-7xl mx-auto px-6">
          {/* Section Header */}
          <div className="text-center mb-20">
            <h2 className="text-4xl font-extrabold text-gray-900">Features</h2>
            <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
              Discover the tools that make CloudFlow a powerful platform for
              developers and teams.
            </p>
          </div>

          <div className="space-y-32">
            {/* Feature 1: Compute */}
            <div className="flex flex-col md:flex-row items-center gap-10">
              <div className="flex-1 text-center md:text-left">
                <h3 className="text-3xl font-bold text-gray-900">Compute Power</h3>
                <p className="mt-4 text-lg text-gray-600">
                  Run CPU and GPU workloads on demand with secure, isolated compute
                  instances tailored for your applications.
                </p>
              </div>
              <motion.div
                initial={{ opacity: 0, x: 100 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 1, ease: "easeOut" }}
                viewport={{ once: true }}
                className="flex-1 flex justify-center"
              >
                <Server className="w-40 h-40 text-blue-500 animate-bounce" />
              </motion.div>
            </div>

            {/* Feature 2: Static Hosting */}
            <div className="flex flex-col md:flex-row-reverse items-center gap-10">
              <div className="flex-1 text-center md:text-left">
                <h3 className="text-3xl font-bold text-gray-900">Static Hosting</h3>
                <p className="mt-4 text-lg text-gray-600">
                  Upload your static websites or React apps and get a live public
                  URL instantly — no configs needed.
                </p>
              </div>
              <motion.div
                initial={{ opacity: 0, x: -100 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 1, ease: "easeOut" }}
                viewport={{ once: true }}
                className="flex-1 flex justify-center"
              >
                <motion.div
                  animate={{ rotate: [0, 15, -15, 0] }}
                  transition={{ repeat: Infinity, duration: 4 }}
                  className="w-40 h-40 bg-gradient-to-r from-blue-400 to-indigo-500 rounded-lg shadow-xl flex items-center justify-center text-white text-xl font-bold"
                >
                  HTML
                </motion.div>
              </motion.div>
            </div>

            {/* Feature 3: Analytics */}
            <div className="flex flex-col md:flex-row items-center gap-10">
              <div className="flex-1 text-center md:text-left">
                <h3 className="text-3xl font-bold text-gray-900">Analytics</h3>
                <p className="mt-4 text-lg text-gray-600">
                  Gain insights into usage, performance, and costs with real-time
                  dashboards powered by CloudFlow analytics.
                </p>
              </div>
              <motion.div
                initial={{ opacity: 0, x: 100 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 1, ease: "easeOut" }}
                viewport={{ once: true }}
                className="flex-1 flex justify-center"
              >
                <motion.div
                  animate={{ scale: [1, 1.1, 1] }}
                  transition={{ repeat: Infinity, duration: 3 }}
                  className="w-40 h-40 flex items-center justify-center"
                >
                  <BarChart className="w-32 h-32 text-purple-500" />
                </motion.div>
              </motion.div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}


