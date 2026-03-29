/**
 * animations.js — Visual effects for the Water Sort Puzzle Game
 * Handles pour effects, shake, win celebration, confetti.
 */

"use strict";

const Animations = (() => {

  // ── Pour splash particles ──────────────────────────────────────────
  function pourEffect(srcIdx, dstIdx) {
    const wraps = document.querySelectorAll(".tube-wrap");
    const srcWrap = wraps[srcIdx];
    const dstWrap = wraps[dstIdx];
    if (!srcWrap || !dstWrap) return;

    const srcRect = srcWrap.getBoundingClientRect();
    const dstRect = dstWrap.getBoundingClientRect();

    // Get the liquid color from src tube top layer
    const srcTube = srcWrap.querySelector(".tube");
    const topLayer = srcTube ? srcTube.lastElementChild : null;
    const color = topLayer
      ? getComputedStyle(topLayer).backgroundImage.match(/rgba?\([^)]+\)/)?.[0] || "#00d4ff"
      : "#00d4ff";

    // Create arc particles
    const numParticles = 8;
    for (let i = 0; i < numParticles; i++) {
      setTimeout(() => {
        const particle = document.createElement("div");
        particle.className = "pour-splash";

        const startX = srcRect.left + srcRect.width / 2;
        const startY = srcRect.top;
        const endX   = dstRect.left + dstRect.width / 2;
        const endY   = dstRect.top + dstRect.height * 0.3;

        particle.style.cssText = `
          left: ${startX}px; top: ${startY}px;
          background: ${color};
          width: ${4 + Math.random() * 5}px;
          height: ${4 + Math.random() * 5}px;
          box-shadow: 0 0 6px ${color};
        `;

        document.body.appendChild(particle);

        // Animate along arc
        const duration = 400 + Math.random() * 100;
        const jitter = (Math.random() - 0.5) * 30;
        particle.animate([
          { transform: `translate(0, 0) scale(1)`, opacity: 1 },
          { transform: `translate(${(endX - startX) / 2 + jitter}px, ${-40}px) scale(1.3)`, opacity: 1 },
          { transform: `translate(${endX - startX}px, ${endY - startY}px) scale(0.5)`, opacity: 0 },
        ], { duration, easing: "cubic-bezier(.4,0,.2,1)" }).onfinish = () => particle.remove();
      }, i * 40);
    }

    // Ripple at destination
    setTimeout(() => rippleEffect(dstWrap), 250);
  }

  // ── Ripple ─────────────────────────────────────────────────────────
  function rippleEffect(wrap) {
    const ripple = document.createElement("div");
    const rect = wrap.getBoundingClientRect();
    ripple.style.cssText = `
      position: fixed;
      left: ${rect.left + rect.width / 2}px;
      top: ${rect.top + rect.height / 2}px;
      width: 10px; height: 10px;
      border: 2px solid rgba(0,212,255,.8);
      border-radius: 50%;
      transform: translate(-50%, -50%);
      pointer-events: none; z-index: 500;
    `;
    document.body.appendChild(ripple);
    ripple.animate([
      { transform: "translate(-50%,-50%) scale(1)", opacity: 1 },
      { transform: "translate(-50%,-50%) scale(5)", opacity: 0 },
    ], { duration: 500, easing: "ease-out" }).onfinish = () => ripple.remove();
  }

  // ── Shake for invalid moves ────────────────────────────────────────
  function shakeEffect(idx) {
    const wraps = document.querySelectorAll(".tube-wrap");
    const wrap = wraps[idx];
    if (!wrap) return;
    wrap.animate([
      { transform: "translateX(0)" },
      { transform: "translateX(-8px)" },
      { transform: "translateX(8px)" },
      { transform: "translateX(-6px)" },
      { transform: "translateX(6px)" },
      { transform: "translateX(0)" },
    ], { duration: 320, easing: "ease-out" });
  }

  // ── Win celebration ────────────────────────────────────────────────
  function winCelebration() {
    const colors = ["#00d4ff","#7b2fff","#00ff88","#ffd700","#ff4466","#ff6a00"];
    for (let i = 0; i < 80; i++) {
      setTimeout(() => spawnConfetti(colors[i % colors.length]), i * 30);
    }

    // Flash all tubes
    document.querySelectorAll(".tube-wrap").forEach((wrap, i) => {
      setTimeout(() => {
        wrap.animate([
          { transform: "scale(1)" },
          { transform: "scale(1.15)" },
          { transform: "scale(1)" },
        ], { duration: 400, easing: "ease-in-out" });
      }, i * 60);
    });
  }

  function spawnConfetti(color) {
    const el = document.createElement("div");
    el.style.cssText = `
      position: fixed; z-index: 600; pointer-events: none;
      left: ${Math.random() * 100}vw;
      top: -10px;
      width: ${5 + Math.random() * 8}px;
      height: ${5 + Math.random() * 8}px;
      background: ${color};
      border-radius: ${Math.random() > 0.5 ? "50%" : "2px"};
      opacity: 1;
    `;
    document.body.appendChild(el);

    const duration = 1200 + Math.random() * 1000;
    const drift = (Math.random() - 0.5) * 200;
    el.animate([
      { transform: `translate(0, 0) rotate(0deg)`, opacity: 1 },
      { transform: `translate(${drift}px, 110vh) rotate(${Math.random() * 720}deg)`, opacity: 0 },
    ], { duration, easing: "ease-in" }).onfinish = () => el.remove();
  }

  // ── Selection pulse ────────────────────────────────────────────────
  function pulseEffect(idx) {
    const wraps = document.querySelectorAll(".tube-wrap");
    const wrap = wraps[idx];
    if (!wrap) return;
    wrap.animate([
      { boxShadow: "0 0 0 0 rgba(0,212,255,0)" },
      { boxShadow: "0 0 0 12px rgba(0,212,255,.3)" },
      { boxShadow: "0 0 0 0 rgba(0,212,255,0)" },
    ], { duration: 600, easing: "ease-out" });
  }

  return { pourEffect, shakeEffect, winCelebration, rippleEffect, pulseEffect };
})();