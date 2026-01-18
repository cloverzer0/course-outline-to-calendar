"use client";

import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useState } from "react";

function FloatingPaths({ position }: { position: number }) {
  const paths = Array.from({ length: 36 }, (_, i) => ({
    id: i,
    d: `M-${380 - i * 5 * position} -${189 + i * 6}C-${
      380 - i * 5 * position
    } -${189 + i * 6} -${312 - i * 5 * position} ${216 - i * 6} ${
      152 - i * 5 * position
    } ${343 - i * 6}C${616 - i * 5 * position} ${470 - i * 6} ${
      684 - i * 5 * position
    } ${875 - i * 6} ${684 - i * 5 * position} ${875 - i * 6}`,
    width: 0.5 + i * 0.03,
  }));

  return (
    <div className="absolute inset-0 z-0 pointer-events-none">
      <svg
        className="w-full h-full text-foreground opacity-30"
        viewBox="0 0 696 316"
        fill="none"
      >
        <title>Background Paths</title>
        {paths.map((path) => (
          <motion.path
            key={path.id}
            d={path.d}
            stroke="currentColor"
            strokeWidth={path.width}
            initial={{ pathLength: 0.3, opacity: 0.4 }}
            animate={{
              pathLength: 1,
              opacity: [0.2, 0.5, 0.2],
              pathOffset: [0, 1, 0],
            }}
            transition={{
              duration: 20 + Math.random() * 10,
              repeat: Infinity,
              ease: "linear",
            }}
          />
        ))}
      </svg>
    </div>
  );
}

export function BackgroundPaths({
  title = "Course Outline to Calendar",
  onUploadClick,
  uploadBox,
}: {
  title?: string;
  onUploadClick?: () => void;
  uploadBox?: React.ReactNode;
}) {
  const [showUploadBox, setShowUploadBox] = useState(false);
  const words = title.split(" ");

  const handleUploadClick = () => {
    setShowUploadBox(true);
    onUploadClick?.();
  };

  return (
    <div className="relative min-h-screen w-full flex items-center justify-center overflow-hidden bg-background text-foreground">
      {/* Animated background */}
      <FloatingPaths position={1} />
      <FloatingPaths position={-1} />

      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 md:px-6 text-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.5 }}
          className="max-w-4xl mx-auto"
        >
          <h1 className="text-5xl sm:text-7xl md:text-8xl font-bold mb-8 tracking-tighter">
            {words.map((word, wordIndex) => (
              <span key={wordIndex} className="inline-block mr-4 last:mr-0">
                {word.split("").map((letter, letterIndex) => (
                  <motion.span
                    key={`${wordIndex}-${letterIndex}`}
                    initial={{ y: 80, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{
                      delay: wordIndex * 0.12 + letterIndex * 0.035,
                      type: "spring",
                      stiffness: 140,
                      damping: 22,
                    }}
                    className="inline-block text-transparent bg-clip-text
                    bg-gradient-to-r from-foreground to-foreground/70"
                  >
                    {letter}
                  </motion.span>
                ))}
              </span>
            ))}
          </h1>

          {/* CTA or Upload Box */}
          <div className="mt-8 flex justify-center">
            {!showUploadBox ? (
              <Button
                type="button"
                onClick={handleUploadClick}
                className="rounded-2xl px-10 py-6 text-lg font-semibold
                bg-foreground text-background
                hover:bg-foreground/90
                transition-all duration-300
                shadow-lg hover:shadow-xl"
              >
                Upload PDF
                <span className="ml-3">→</span>
              </Button>
            ) : (
              uploadBox
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
