import { motion } from "framer-motion";

export default function UserProfileModal() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-white rounded-2xl shadow-xl p-8 w-[600px]"
    >
      <h2 className="text-2xl font-bold mb-6 text-gray-800">User Profile</h2>
      <p className="text-gray-600">Update account settings, personal info, and security details.</p>
    </motion.div>
  );
}
