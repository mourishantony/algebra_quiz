/**
 * Algebra Quiz — Main JavaScript Engine
 * Manages quiz state machine, API calls, timer, and animations.
 * No database — fully stateless; all session state lives in the browser.
 */

'use strict';

// ─── Configuration ────────────────────────────────────────────────────────────
const CONFIG = {
  totalQuestions: 10,
  timerSeconds: 30,
  apiBase: '',
};

// ─── State ────────────────────────────────────────────────────────────────────
const state = {
  screen: 'welcome',      // 'welcome' | 'quiz' | 'results'
  playerName: '',
  difficulty: 'medium',
  category: null,
  questionIndex: 0,
  score: 0,
  attempts: [],
  currentQuestion: null,
  usedHint: false,
  answered: false,
  timerInterval: null,
  timerLeft: CONFIG.timerSeconds,
  sessionStartTime: null,
  questionStartTime: null,
};

// ─── DOM References ───────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);

const screens = {
  welcome: $('welcome-screen'),
  quiz:    $('quiz-screen'),
  results: $('results-screen'),
};

// Welcome
const nameInput       = $('player-name');
const startBtn        = $('start-btn');
const diffPills       = document.querySelectorAll('.diff-pill');
const catPills        = document.querySelectorAll('.cat-pill');

// Quiz
const qCounter        = $('q-counter');
const qCategoryBadge  = $('q-category-badge');
const progressFill    = $('progress-fill');
const timerText       = $('timer-text');
const timerRingFg     = $('timer-ring-fg');
const scoreLiveVal    = $('score-live-val');
const questionText    = $('question-text');
const answerInput     = $('answer-input');
const submitBtn       = $('submit-btn');
const hintBtn         = $('hint-btn');
const nextBtn         = $('next-btn');
const hintBox         = $('hint-box');
const hintText        = $('hint-text');
const feedbackBanner  = $('feedback-banner');
const feedbackIcon    = $('feedback-icon');
const feedbackTitle   = $('feedback-title');
const feedbackExp     = $('feedback-explanation');

// Results
const resultsTitle    = $('results-title');
const resultsEmoji    = $('results-emoji');
const resultsSub      = $('results-subtitle');
const scoreHeroNum    = $('score-hero-num');
const scoreHeroTotal  = $('score-hero-total');
const gradeBadge      = $('grade-badge');
const scoreRingFill   = $('score-ring-fill');
const statCorrect     = $('stat-correct');
const statWrong       = $('stat-wrong');
const statPercent     = $('stat-percent');
const statTime        = $('stat-time');
const categoryBreakdown = $('category-breakdown');
const reviewList      = $('review-list');
const playAgainBtn    = $('play-again-btn');

// Toast
const toast = $('toast');

// ─── Screen Management ────────────────────────────────────────────────────────
function showScreen(name) {
  Object.entries(screens).forEach(([key, el]) => {
    el.classList.remove('active');
  });
  const el = screens[name];
  el.classList.remove('active');
  // Force reflow for animation restart
  void el.offsetWidth;
  el.classList.add('active');
  state.screen = name;
}

// ─── Welcome Screen ───────────────────────────────────────────────────────────
function initWelcomeScreen() {
  // Difficulty pills
  diffPills.forEach(pill => {
    pill.addEventListener('click', () => {
      diffPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      state.difficulty = pill.dataset.diff;
    });
  });

  // Category pills
  catPills.forEach(pill => {
    pill.addEventListener('click', () => {
      if (pill.classList.contains('active')) {
        pill.classList.remove('active');
        state.category = null;
      } else {
        catPills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active-accent');
        state.category = pill.dataset.cat;
      }
    });
  });

  // Start button
  startBtn.addEventListener('click', () => {
    const name = nameInput.value.trim();
    if (!name) {
      nameInput.classList.add('shake');
      nameInput.addEventListener('animationend', () => nameInput.classList.remove('shake'), { once: true });
      nameInput.focus();
      showToast('Please enter your name to start! 📝');
      return;
    }
    state.playerName = name;
    startQuiz();
  });

  nameInput.addEventListener('keydown', e => {
    if (e.key === 'Enter') startBtn.click();
  });
}

// ─── Quiz Logic ───────────────────────────────────────────────────────────────
function startQuiz() {
  state.questionIndex = 0;
  state.score = 0;
  state.attempts = [];
  state.sessionStartTime = Date.now();
  showScreen('quiz');
  loadNextQuestion();
}

async function loadNextQuestion() {
  // Reset UI
  state.answered = false;
  state.usedHint = false;
  state.currentQuestion = null;
  answerInput.value = '';
  answerInput.disabled = false;
  submitBtn.disabled = false;
  nextBtn.style.display = 'none';
  hintBtn.style.display = 'inline-flex';
  hintBtn.disabled = false;
  hintBox.classList.remove('visible');
  feedbackBanner.className = 'feedback-banner';
  feedbackBanner.style.display = 'none';

  // Update progress
  const progress = (state.questionIndex / CONFIG.totalQuestions) * 100;
  progressFill.style.width = progress + '%';
  qCounter.textContent = `Question ${state.questionIndex + 1} of ${CONFIG.totalQuestions}`;
  scoreLiveVal.textContent = `${state.score}/${state.questionIndex}`;

  // Show loading
  questionText.innerHTML = `<span style="color:var(--clr-text-muted)">Loading question <span class="loading-dots"><span></span><span></span><span></span></span></span>`;
  qCategoryBadge.textContent = '...';

  try {
    const res = await fetch('/api/generate-question/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ difficulty: state.difficulty, category: state.category }),
    });
    const data = await res.json();
    if (!data.success) throw new Error('Server error');

    state.currentQuestion = data.data;
    displayQuestion(data.data);
    startTimer();

  } catch (err) {
    questionText.innerHTML = `<span style="color:var(--clr-danger)">Failed to load question. Please check your connection.</span>`;
    console.error(err);
  }
}

function displayQuestion(q) {
  questionText.innerHTML = q.question;
  qCategoryBadge.textContent = q.category;
  state.questionStartTime = Date.now();

  // Animate question in
  questionText.style.opacity = '0';
  questionText.style.transform = 'translateY(8px)';
  requestAnimationFrame(() => {
    questionText.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    questionText.style.opacity = '1';
    questionText.style.transform = 'translateY(0)';
  });

  answerInput.focus();
}

function startTimer() {
  clearInterval(state.timerInterval);
  state.timerLeft = CONFIG.timerSeconds;
  updateTimerDisplay();

  state.timerInterval = setInterval(() => {
    state.timerLeft--;
    updateTimerDisplay();

    if (state.timerLeft <= 0) {
      clearInterval(state.timerInterval);
      if (!state.answered) {
        timeUp();
      }
    }
  }, 1000);
}

function updateTimerDisplay() {
  const t = state.timerLeft;
  timerText.textContent = t;

  // Ring animation (circumference ≈ 163 for r=26)
  const circ = 163;
  const offset = circ - (t / CONFIG.timerSeconds) * circ;
  timerRingFg.style.strokeDashoffset = offset;

  // Color states
  timerRingFg.classList.remove('warning', 'danger');
  if (t <= 5) timerRingFg.classList.add('danger');
  else if (t <= 10) timerRingFg.classList.add('warning');
}

function timeUp() {
  state.answered = true;
  answerInput.disabled = true;
  submitBtn.disabled = true;

  const q = state.currentQuestion;
  const timeTaken = Math.round((Date.now() - state.questionStartTime) / 1000);
  state.attempts.push({
    question: stripHTML(q.question),
    category: q.category,
    correct_answer: q.answer,
    user_answer: '(no answer)',
    is_correct: false,
    used_hint: state.usedHint,
    time_taken: timeTaken,
  });

  showFeedback(false, "Time's up! ⏰", q.explanation, true);
  nextBtn.style.display = 'inline-flex';
  hintBtn.style.display = 'none';
  scoreLiveVal.textContent = `${state.score}/${state.questionIndex + 1}`;
}

async function submitAnswer() {
  if (state.answered || !state.currentQuestion) return;

  const userAnswer = answerInput.value.trim();
  if (!userAnswer) {
    answerInput.classList.add('shake');
    answerInput.addEventListener('animationend', () => answerInput.classList.remove('shake'), { once: true });
    return;
  }

  clearInterval(state.timerInterval);
  state.answered = true;
  answerInput.disabled = true;
  submitBtn.disabled = true;
  hintBtn.disabled = true;

  const q = state.currentQuestion;
  const timeTaken = Math.round((Date.now() - state.questionStartTime) / 1000);

  try {
    const res = await fetch('/api/check-answer/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_answer: userAnswer,
        correct_answer: q.answer,
        explanation: q.explanation,
      }),
    });
    const data = await res.json();
    const isCorrect = data.is_correct;

    if (isCorrect) {
      state.score++;
      answerInput.classList.add('sparkle');
      answerInput.addEventListener('animationend', () => answerInput.classList.remove('sparkle'), { once: true });
      showFeedback(true, 'Correct! 🎉', q.explanation);
    } else {
      answerInput.classList.add('shake');
      answerInput.addEventListener('animationend', () => answerInput.classList.remove('shake'), { once: true });
      showFeedback(false, `Incorrect — correct answer: ${q.answer}`, q.explanation);
    }

    state.attempts.push({
      question: stripHTML(q.question),
      category: q.category,
      correct_answer: q.answer,
      user_answer: userAnswer,
      is_correct: isCorrect,
      used_hint: state.usedHint,
      time_taken: timeTaken,
    });

    scoreLiveVal.textContent = `${state.score}/${state.questionIndex + 1}`;
    nextBtn.style.display = 'inline-flex';
    hintBtn.style.display = 'none';

  } catch (err) {
    console.error('Answer check failed:', err);
    showToast('Network error — please try again');
    state.answered = false;
    answerInput.disabled = false;
    submitBtn.disabled = false;
  }
}

function showFeedback(isCorrect, title, explanation, timeup = false) {
  feedbackBanner.style.display = 'none';
  feedbackBanner.className = 'feedback-banner ' + (isCorrect ? 'correct' : 'wrong');
  feedbackIcon.textContent = isCorrect ? '✅' : (timeup ? '⏱️' : '❌');
  feedbackTitle.textContent = title;
  feedbackExp.innerHTML = explanation;
  feedbackBanner.style.display = 'flex';
}

function showHint() {
  if (!state.currentQuestion) return;
  state.usedHint = true;
  hintText.textContent = state.currentQuestion.hint;
  hintBox.classList.add('visible');
  hintBtn.disabled = true;
  hintBtn.textContent = '💡 Hint Used';
}

function nextQuestion() {
  state.questionIndex++;
  if (state.questionIndex >= CONFIG.totalQuestions) {
    endQuiz();
  } else {
    loadNextQuestion();
  }
}

// ─── End Quiz & Results ───────────────────────────────────────────────────────
function endQuiz() {
  clearInterval(state.timerInterval);
  const totalTime = Math.round((Date.now() - state.sessionStartTime) / 1000);
  showScreen('results');
  renderResults(totalTime);
  if (state.score === CONFIG.totalQuestions) {
    setTimeout(launchConfetti, 600);
  }
}

function renderResults(totalTime) {
  const pct = Math.round((state.score / CONFIG.totalQuestions) * 100);
  const wrong = CONFIG.totalQuestions - state.score;

  // Grade
  let grade = 'F';
  if (pct >= 90) grade = 'A+';
  else if (pct >= 80) grade = 'A';
  else if (pct >= 70) grade = 'B';
  else if (pct >= 60) grade = 'C';
  else if (pct >= 50) grade = 'D';

  // Emoji & messages
  const messages = {
    'A+': { emoji: '🏆', title: 'Perfect Score!', sub: `Incredible, ${state.playerName}! You aced every question!` },
    'A':  { emoji: '🌟', title: 'Excellent!',     sub: `Outstanding work, ${state.playerName}! Almost perfect!` },
    'B':  { emoji: '👏', title: 'Well Done!',     sub: `Great job, ${state.playerName}! Keep it up!` },
    'C':  { emoji: '👍', title: 'Good Effort!',   sub: `Not bad, ${state.playerName}! Practice makes perfect.` },
    'D':  { emoji: '📚', title: 'Keep Trying!',   sub: `Keep studying, ${state.playerName}! You'll get there!` },
    'F':  { emoji: '💪', title: "Don't Give Up!", sub: `Algebra takes practice, ${state.playerName}! Try again!` },
  };

  const msg = messages[grade] || messages['F'];
  resultsEmoji.textContent = msg.emoji;
  resultsTitle.textContent = msg.title;
  resultsSub.textContent = msg.sub;

  // Score ring animation
  scoreHeroNum.textContent = state.score;
  scoreHeroTotal.textContent = `/ ${CONFIG.totalQuestions}`;

  const circ = 440;
  const offset = circ - (pct / 100) * circ;
  setTimeout(() => {
    scoreRingFill.style.strokeDashoffset = offset;
  }, 300);

  // Grade class
  scoreRingFill.className = 'score-ring-fill';
  gradeBadge.className = 'grade-badge';
  if (grade === 'A+' || grade === 'A') {
    scoreRingFill.classList.add('grade-a');
    gradeBadge.classList.add('a');
    if (grade === 'A+') gradeBadge.classList.add('a-plus');
  } else if (grade === 'B') {
    scoreRingFill.classList.add('grade-b');
    gradeBadge.classList.add('b');
  } else if (grade === 'F') {
    scoreRingFill.classList.add('grade-f');
    gradeBadge.classList.add('f');
  }

  gradeBadge.textContent = grade;
  statCorrect.textContent = state.score;
  statWrong.textContent = wrong;
  statPercent.textContent = pct + '%';
  statTime.textContent = formatTime(totalTime);

  const resultDiffEl = $('result-difficulty');
  if (resultDiffEl) resultDiffEl.textContent = state.difficulty;

  // Category breakdown
  renderCategoryBreakdown();

  // Review list
  renderReviewList();
}

function renderCategoryBreakdown() {
  const catMap = {};
  state.attempts.forEach(a => {
    if (!catMap[a.category]) catMap[a.category] = { correct: 0, total: 0 };
    catMap[a.category].total++;
    if (a.is_correct) catMap[a.category].correct++;
  });

  const rows = Object.entries(catMap).map(([cat, data]) => {
    const pct = data.total ? Math.round((data.correct / data.total) * 100) : 0;
    return `
      <div class="category-row">
        <span class="category-label">${cat}</span>
        <div class="category-bar-wrap">
          <div class="category-bar-fill" style="width: 0%" data-pct="${pct}"></div>
        </div>
        <span class="category-fraction">${data.correct}/${data.total}</span>
      </div>`;
  }).join('');

  categoryBreakdown.innerHTML = rows;

  // Animate bars in
  setTimeout(() => {
    categoryBreakdown.querySelectorAll('.category-bar-fill').forEach(bar => {
      bar.style.width = bar.dataset.pct + '%';
    });
  }, 400);
}

function renderReviewList() {
  const items = state.attempts.map((a, i) => {
    const cls = a.is_correct ? 'correct' : 'wrong';
    const icon = a.is_correct ? '✅' : '❌';
    const yoursCls = a.is_correct ? 'yours correct-yours' : 'yours';
    return `
      <div class="review-item ${cls}" id="review-item-${i}">
        <div class="review-item-header" onclick="toggleReview(${i})">
          <span class="review-icon">${icon}</span>
          <span class="review-q-text">Q${i+1}: ${a.question.replace(/<[^>]+>/g, '')}</span>
          <span class="review-chevron">▼</span>
        </div>
        <div class="review-item-body">
          <div class="review-answer-row">
            <div>
              <div style="font-size:0.72rem;color:var(--clr-text-muted);margin-bottom:0.3rem;text-transform:uppercase;letter-spacing:.08em">Your Answer</div>
              <div class="review-answer-box ${yoursCls}">${a.user_answer}</div>
            </div>
            <div>
              <div style="font-size:0.72rem;color:var(--clr-text-muted);margin-bottom:0.3rem;text-transform:uppercase;letter-spacing:.08em">Correct Answer</div>
              <div class="review-answer-box correct-ans">${a.correct_answer}</div>
            </div>
          </div>
          ${a.used_hint ? '<div style="font-size:0.8rem;color:var(--clr-warning);margin-bottom:0.5rem">💡 Hint was used</div>' : ''}
          <div class="review-explanation">${a.category}</div>
        </div>
      </div>`;
  }).join('');

  reviewList.innerHTML = items || '<p style="color:var(--clr-text-muted);text-align:center;padding:1rem">No attempts recorded.</p>';
}



// ─── Review Accordion ─────────────────────────────────────────────────────────
window.toggleReview = function(index) {
  const item = $(`review-item-${index}`);
  item.classList.toggle('open');
};

// ─── Confetti ─────────────────────────────────────────────────────────────────
function launchConfetti() {
  const canvas = $('confetti-canvas');
  const ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  const colors = ['#a855f7', '#22d3ee', '#facc15', '#34d399', '#f472b6', '#60a5fa'];
  const particles = Array.from({ length: 140 }, () => ({
    x: Math.random() * canvas.width,
    y: -10,
    r: Math.random() * 7 + 3,
    d: Math.random() * 80 + 40,
    color: colors[Math.floor(Math.random() * colors.length)],
    tilt: Math.random() * 10 - 10,
    tiltAngleInc: (Math.random() * 0.07 + 0.05),
    tiltAngle: 0,
    speedY: Math.random() * 3 + 2,
    speedX: Math.random() * 2 - 1,
  }));

  let frame = 0;
  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => {
      ctx.beginPath();
      ctx.lineWidth = p.r;
      ctx.strokeStyle = p.color;
      ctx.moveTo(p.x + p.tilt + p.r / 2, p.y);
      ctx.lineTo(p.x + p.tilt, p.y + p.tilt + p.r / 2);
      ctx.stroke();
    });
    update();
    frame++;
    if (frame < 300) requestAnimationFrame(draw);
    else ctx.clearRect(0, 0, canvas.width, canvas.height);
  }

  function update() {
    particles.forEach(p => {
      p.tiltAngle += p.tiltAngleInc;
      p.y += p.speedY;
      p.x += p.speedX;
      p.tilt = Math.sin(p.tiltAngle) * 12;
      if (p.y > canvas.height) {
        p.y = -10;
        p.x = Math.random() * canvas.width;
      }
    });
  }

  draw();
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
}

function stripHTML(html) {
  const tmp = document.createElement('div');
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText || '';
}

function escapeHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function showToast(msg) {
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 3000);
}

// ─── Event Listeners ──────────────────────────────────────────────────────────
function initEventListeners() {
  submitBtn.addEventListener('click', submitAnswer);

  answerInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !state.answered) submitAnswer();
  });

  hintBtn.addEventListener('click', showHint);

  nextBtn.addEventListener('click', nextQuestion);

  playAgainBtn.addEventListener('click', () => {
    showScreen('welcome');
  });

  // Keyboard shortcut: H for hint, Enter for next
  document.addEventListener('keydown', e => {
    if (state.screen !== 'quiz') return;
    if (e.key === 'h' && !state.answered && document.activeElement !== answerInput) {
      showHint();
    }
    if (e.key === 'Enter' && state.answered && nextBtn.style.display !== 'none') {
      nextQuestion();
    }
  });
}

// ─── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initWelcomeScreen();
  initEventListeners();
  showScreen('welcome');
});
