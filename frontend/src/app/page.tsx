"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-provider";
import "./landing.css";

function TypingText() {
  const texts = [
    "Finish Q3 report by Thursday",
    "Call mom this Sunday evening",
    "Book flight for the conference",
    "Review team PRs before standup",
  ];
  const [display, setDisplay] = useState(texts[0]);
  const tIdx = useRef(0);
  const cIdx = useRef(texts[0].length);
  const deleting = useRef(false);

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;

    function step() {
      const target = texts[tIdx.current];
      if (!deleting.current) {
        cIdx.current++;
        setDisplay(target.slice(0, cIdx.current));
        if (cIdx.current === target.length) {
          deleting.current = true;
          timer = setTimeout(step, 2200);
          return;
        }
      } else {
        cIdx.current--;
        setDisplay(target.slice(0, cIdx.current));
        if (cIdx.current === 0) {
          deleting.current = false;
          tIdx.current = (tIdx.current + 1) % texts.length;
          timer = setTimeout(step, 380);
          return;
        }
      }
      timer = setTimeout(step, deleting.current ? 38 : 68);
    }

    timer = setTimeout(step, 1400);
    return () => clearTimeout(timer);
  }, []);

  return <span className="mockup-input-text">{display}</span>;
}

function FadeUp({
  children,
  className = "",
  delay = 0,
}: {
  children: React.ReactNode;
  className?: string;
  delay?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("in");
            observer.unobserve(e.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -48px 0px" }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      className={`fade-up ${className}`}
      style={{ transitionDelay: `${delay}s` }}
    >
      {children}
    </div>
  );
}

export default function Home() {
  const [scrolled, setScrolled] = useState(false);
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 24);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className="landing-page">
      {/* NAV */}
      <nav className={`landing-nav ${scrolled ? "scrolled" : ""}`}>
        <Link className="logo" href="#">
          Taska<span>.</span>
        </Link>
        <ul>
          <li><a href="#features">Features</a></li>
          <li><a href="#how">How it works</a></li>
          <li><a href="#testimonials">Testimonials</a></li>
        </ul>
        <div className="nav-actions">
          {isAuthenticated ? (
            <Link className="btn btn-primary" href="/dashboard">Dashboard</Link>
          ) : (
            <>
              <Link className="btn btn-ghost" href="/auth/signin">Sign in</Link>
              <Link className="btn btn-primary" href="/auth/signup">Get started free</Link>
            </>
          )}
        </div>
      </nav>

      {/* HERO */}
      <div className="hero">
        <div className="hero-left">
          <div className="hero-badge">
            <div className="badge-dot"></div>
            Now with AI-powered intelligence
          </div>
          <h1>Think less.<br />Do <em>more.</em></h1>
          <p className="hero-desc">
            Taska turns your scattered to-dos into a razor-sharp daily plan. Just tell it what&apos;s on your mind — AI handles the organizing, prioritizing, and scheduling.
          </p>
          <div className="hero-actions">
            {isAuthenticated ? (
              <Link className="btn btn-primary btn-lg" href="/dashboard">Go to Dashboard</Link>
            ) : (
              <Link className="btn btn-primary btn-lg" href="/auth/signup">Start for free</Link>
            )}
            <Link className="btn btn-outline btn-lg" href="#how">Watch demo</Link>
          </div>
          <div className="hero-note">
            <span>No credit card required</span>
            <div className="hero-note-dot"></div>
            <span>Free forever plan</span>
            <div className="hero-note-dot"></div>
            <span>Setup in 60 seconds</span>
          </div>
        </div>

        <div className="hero-visual">
          <div className="mockup-glow"></div>

          {/* Floating stat card */}
          <div className="float-card">
            <div className="float-eyebrow">Done today</div>
            <div className="float-stat">12</div>
            <div className="float-sub">↑ 3 more than yesterday</div>
            <div className="float-progress"><div className="float-fill"></div></div>
          </div>

          {/* Main app mockup */}
          <div className="mockup-main">
            <div className="mockup-bar">
              <span className="mockup-bar-title">Today</span>
              <span className="mockup-bar-date">Sat, May 17</span>
            </div>

            <div className="mockup-progress">
              <div className="prog-label">
                <span>Daily progress</span>
                <span>7 of 12 done</span>
              </div>
              <div className="prog-track">
                <div className="prog-fill"></div>
              </div>
            </div>

            <div className="mockup-input-wrap">
              <div className="mockup-input">
                <svg className="input-icon" viewBox="0 0 24 24">
                  <path d="M12 20h9"></path>
                  <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
                </svg>
                <TypingText />
                <div className="cursor"></div>
              </div>
            </div>

            <div className="task-list">
              <div className="task-row">
                <div className="task-cb"></div>
                <span className="task-label">Review product roadmap with team</span>
                <span className="ai-tag tag-high">High</span>
              </div>
              <div className="task-row">
                <div className="task-cb"></div>
                <span className="task-label">Prepare slides for investor call</span>
                <span className="ai-tag tag-high">High</span>
              </div>
              <div className="task-row">
                <div className="task-cb"></div>
                <span className="task-label">Schedule dentist appointment</span>
                <span className="ai-tag tag-med">Medium</span>
              </div>
              <div className="task-row">
                <div className="task-cb done"></div>
                <span className="task-label done">Send invoice to client</span>
                <span className="ai-tag tag-done">Done</span>
              </div>
            </div>

            <div className="ai-suggest">
              <div className="ai-suggest-hd">
                <div className="ai-dot"></div>
                AI Insight
              </div>
              <div className="ai-suggest-text">
                Investor call is in 3 hours. I&apos;ve moved slide prep to the top and cleared your afternoon for prep time.
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* TRUST BAR */}
      <div className="trust-bar">
        <div className="trust-inner">
          <span className="trust-txt">Trusted by teams at</span>
          <div className="trust-div"></div>
          <div className="trust-logos">
            <span className="trust-logo">Veritas</span>
            <span className="trust-logo">Meridian</span>
            <span className="trust-logo">Crestwood</span>
            <span className="trust-logo">Arcana</span>
            <span className="trust-logo">Solstice</span>
          </div>
        </div>
      </div>

      {/* FEATURES */}
      <section id="features">
        <div className="section">
          <FadeUp className="s-head">
            <div className="s-eyebrow">Features</div>
            <h2 className="s-h2">Built for how you <em>actually</em> work</h2>
            <p className="s-sub">No rigid systems. No complex setup. Taska learns your rhythms and gets sharper every day.</p>
          </FadeUp>

          <div className="feat-grid">
            <FadeUp delay={0.08}>
              <div className="feat-card">
                <div className="feat-ico">
                  <svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                </div>
                <h3 className="feat-h3">Natural Language</h3>
                <p className="feat-p">Type like you think. &ldquo;Call mom Sunday evening&rdquo; becomes a structured, scheduled task — no formatting required.</p>
              </div>
            </FadeUp>

            <FadeUp delay={0.17}>
              <div className="feat-card">
                <div className="feat-ico">
                  <svg viewBox="0 0 24 24"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
                </div>
                <h3 className="feat-h3">Smart Prioritization</h3>
                <p className="feat-p">AI reads your deadlines, energy patterns, and dependencies to surface exactly what needs your attention right now.</p>
              </div>
            </FadeUp>

            <FadeUp delay={0.26}>
              <div className="feat-card">
                <div className="feat-ico">
                  <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                </div>
                <h3 className="feat-h3">Time Intelligence</h3>
                <p className="feat-p">Understands context — meetings, habits, soft deadlines — and proactively reshuffles your day when things change.</p>
              </div>
            </FadeUp>

            <FadeUp delay={0.35}>
              <div className="feat-card">
                <div className="feat-ico">
                  <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"></circle><circle cx="12" cy="12" r="8"></circle><line x1="12" y1="2" x2="12" y2="4"></line><line x1="12" y1="20" x2="12" y2="22"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line></svg>
                </div>
                <h3 className="feat-h3">Deep Focus Mode</h3>
                <p className="feat-p">One task. Full screen. Zero noise. Taska hides everything but what deserves your full attention in this moment.</p>
              </div>
            </FadeUp>

            <FadeUp delay={0.44}>
              <div className="feat-card">
                <div className="feat-ico">
                  <svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                </div>
                <h3 className="feat-h3">Weekly Review</h3>
                <p className="feat-p">Every Sunday, a personal digest of wins, slips, and a curated plan for the week ahead — written just for you.</p>
              </div>
            </FadeUp>

            <FadeUp delay={0.53}>
              <div className="feat-card">
                <div className="feat-ico">
                  <svg viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                </div>
                <h3 className="feat-h3">Team Collaboration</h3>
                <p className="feat-p">Share lists, delegate tasks, and track team progress at a glance. AI balances workloads so no one burns out.</p>
              </div>
            </FadeUp>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <div className="section-alt" id="how">
        <div className="section">
          <FadeUp className="s-head">
            <div className="s-eyebrow">How it works</div>
            <h2 className="s-h2">Three steps to clarity</h2>
            <p className="s-sub">From brain dump to done list — Taska removes all friction in between.</p>
          </FadeUp>

          <div className="steps">
            <FadeUp delay={0.08}>
              <div className="step active">
                <div className="step-num">1</div>
                <h3 className="step-h3">Brain dump it all</h3>
                <p className="step-p">Add everything cluttering your mind in seconds. No structure, no formatting — just talk to Taska like a trusted colleague.</p>
              </div>
            </FadeUp>

            <FadeUp delay={0.17}>
              <div className="step">
                <div className="step-num">2</div>
                <h3 className="step-h3">AI organizes it</h3>
                <p className="step-p">Taska categorizes, prioritizes, and schedules — learning your rhythms over time so its suggestions get sharper every week.</p>
              </div>
            </FadeUp>

            <FadeUp delay={0.26}>
              <div className="step">
                <div className="step-num">3</div>
                <h3 className="step-h3">Focus and execute</h3>
                <p className="step-p">Follow the AI-curated daily plan, check things off, and watch your output compound week after week after week.</p>
              </div>
            </FadeUp>
          </div>
        </div>
      </div>

      {/* TESTIMONIALS */}
      <section id="testimonials">
        <div className="section">
          <FadeUp className="s-head">
            <div className="s-eyebrow">Testimonials</div>
            <h2 className="s-h2">People who use Taska <em>love</em> it</h2>
          </FadeUp>

          <div className="testi-grid">
            <FadeUp delay={0.08}>
              <div className="testi-card">
                <div className="testi-stars">
                  {[...Array(5)].map((_, i) => <div key={i} className="star"></div>)}
                </div>
                <p className="testi-quote">I&apos;ve tried every todo app. Taska is the first one that actually reduced my anxiety. The AI prioritization is scarily good — it knows what matters before I do.</p>
                <div className="testi-author">
                  <div className="testi-av">S</div>
                  <div>
                    <div className="testi-name">Sarah K.</div>
                    <div className="testi-role">Product Lead, Veritas</div>
                  </div>
                </div>
              </div>
            </FadeUp>

            <FadeUp delay={0.17}>
              <div className="testi-card">
                <div className="testi-stars">
                  {[...Array(5)].map((_, i) => <div key={i} className="star"></div>)}
                </div>
                <p className="testi-quote">The natural language input changed everything. I say &lsquo;prep for Monday&apos;s board meeting&rsquo; and Taska breaks it into actual steps with deadlines. Wild.</p>
                <div className="testi-author">
                  <div className="testi-av">M</div>
                  <div>
                    <div className="testi-name">Marcus T.</div>
                    <div className="testi-role">Founder, Meridian Labs</div>
                  </div>
                </div>
              </div>
            </FadeUp>

            <FadeUp delay={0.26}>
              <div className="testi-card">
                <div className="testi-stars">
                  {[...Array(5)].map((_, i) => <div key={i} className="star"></div>)}
                </div>
                <p className="testi-quote">We rolled Taska out to our whole engineering team. Within a week, everyone was hitting their deadlines. The AI insight cards are like having a PM in your pocket.</p>
                <div className="testi-author">
                  <div className="testi-av">L</div>
                  <div>
                    <div className="testi-name">Lena M.</div>
                    <div className="testi-role">Engineering Manager, Crestwood</div>
                  </div>
                </div>
              </div>
            </FadeUp>
          </div>
        </div>
      </section>

      {/* CTA */}
      <div className="cta-wrap">
        <div className="cta-inner">
          <div className="cta-orb"></div>
          <div className="cta-left">
            <div className="cta-label">{isAuthenticated ? 'Welcome back' : 'Get started today'}</div>
            <h2 className="cta-h2">Your most productive year starts now</h2>
            <p className="cta-sub">Free forever plan. No card required. Live in 60 seconds.</p>
          </div>
          <div className="cta-right">
            {isAuthenticated ? (
              <Link className="btn btn-white" href="/dashboard">Go to Dashboard →</Link>
            ) : (
              <>
                <Link className="btn btn-white" href="/auth/signup">Start for free →</Link>
                <span className="cta-fine">Or <Link href="#" className="cta-demo-link">book a demo</Link></span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* FOOTER */}
      <footer className="landing-footer">
        <div className="footer-inner">
          <Link className="footer-logo" href="#">Taska<span>.</span></Link>
          <ul className="footer-links">
            <li><a href="#">Privacy</a></li>
            <li><a href="#">Terms</a></li>
            <li><a href="#">Blog</a></li>
            <li><a href="#">Changelog</a></li>
            <li><a href="#">Contact</a></li>
          </ul>
          <span className="footer-copy">© 2026 Taska, Inc.</span>
        </div>
      </footer>
    </div>
  );
}
