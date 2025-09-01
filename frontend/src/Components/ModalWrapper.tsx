import { motion } from "framer-motion";

export default function ModalWrapper({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="rounded-2xl shadow-xl w-full flex justify-center"
    >
      {children}
    </motion.div>
  );
}
