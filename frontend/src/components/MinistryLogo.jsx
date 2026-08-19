import { useState } from "react";
import { MINISTRY_SHORT } from "../branding";

/** Fichier attendu : frontend/public/logo-ministere.png (idéal : 512×512 px) */
const LOGO_SRC = "/logo-ministere.png";

const SIZES = {
  nav: "h-16 w-16 sm:h-20 sm:w-20",
  login: "h-28 w-28 sm:h-36 sm:w-36",
};

const FALLBACK_TEXT = {
  nav: "text-[11px] sm:text-xs",
  login: "text-sm sm:text-base",
};

/**
 * @param {{ size?: "nav" | "login", className?: string, framed?: boolean }} props
 */
export default function MinistryLogo({ size = "nav", className = "", framed = true }) {
  const [failed, setFailed] = useState(false);
  const sizeClass = SIZES[size] || SIZES.nav;
  const textClass = FALLBACK_TEXT[size] || FALLBACK_TEXT.nav;

  const inner = failed ? (
    <div
      className={`${sizeClass} flex shrink-0 items-center justify-center rounded-lg bg-brand-800 text-center font-display font-bold leading-tight text-white ${textClass}`}
      aria-hidden
    >
      {MINISTRY_SHORT.slice(0, 4)}
      <br />
      {MINISTRY_SHORT.slice(4)}
    </div>
  ) : (
    <img
      src={LOGO_SRC}
      alt={`Logo ${MINISTRY_SHORT}`}
      className={`${sizeClass} shrink-0 object-contain`}
      onError={() => setFailed(true)}
    />
  );

  if (!framed) {
    return <div className={className}>{inner}</div>;
  }

  return (
    <div
      className={`flex shrink-0 items-center justify-center rounded-xl border border-slate-200/80 bg-white p-1.5 shadow-sm sm:p-2 ${className}`}
    >
      {inner}
    </div>
  );
}
