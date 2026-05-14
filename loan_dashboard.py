import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Loan Amortization Dashboard", layout="wide")

st.title("📊 Loan Amortization Dashboard")
st.markdown("---")

# Create input columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    loan_amount = st.number_input(
        "Loan Amount (€)",
        min_value=0.0,
        value=100000.0,
        step=1000.0,
        format="%.2f"
    )

with col2:
    interest_rate = st.number_input(
        "Annual Interest Rate (%)",
        min_value=0.0,
        value=5.0,
        step=0.1,
        format="%.2f"
    )

with col3:
    monthly_payment = st.number_input(
        "Monthly Payment (€)",
        min_value=0.0,
        value=1000.0,
        step=50.0,
        format="%.2f"
    )

with col4:
    term_months = st.number_input(
        "Loan Term (months)",
        min_value=1,
        value=360,
        step=12
    )

st.markdown("---")

# Calculate amortization schedule
def calculate_amortization(principal, annual_rate, payment, max_months):
    """Calculate loan amortization schedule"""
    monthly_rate = annual_rate / 100 / 12
    
    schedule = []
    balance = principal
    month = 0
    
    while balance > 0 and month < max_months:
        month += 1
        
        # Calculate interest for this month
        interest_payment = balance * monthly_rate
        
        # Calculate principal payment
        principal_payment = payment - interest_payment
        
        # If payment is less than interest, loan grows
        if principal_payment < 0:
            st.warning("⚠️ Warning: Monthly payment is less than interest! Loan balance will grow.")
            principal_payment = 0
            balance += interest_payment
        else:
            # Reduce balance
            balance -= principal_payment
            
        # Don't let balance go negative
        if balance < 0:
            principal_payment += balance
            balance = 0
            
        schedule.append({
            'Month': month,
            'Payment': payment if balance > 0 or month == 1 else payment + balance,
            'Principal': principal_payment,
            'Interest': interest_payment,
            'Balance': max(0, balance)
        })
        
        if balance <= 0:
            break
    
    return pd.DataFrame(schedule)

# Calculate the schedule
if loan_amount > 0 and monthly_payment > 0:
    df = calculate_amortization(loan_amount, interest_rate, monthly_payment, term_months)
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_paid = df['Payment'].sum()
    total_interest = df['Interest'].sum()
    total_principal = df['Principal'].sum()
    months_to_payoff = len(df)
    
    with col1:
        st.metric("Total Amount Paid", f"€{total_paid:,.2f}")
    
    with col2:
        st.metric("Total Interest Paid", f"€{total_interest:,.2f}")
    
    with col3:
        st.metric("Total Principal Paid", f"€{total_principal:,.2f}")
    
    with col4:
        st.metric("Months to Payoff", f"{months_to_payoff}")
    
    st.markdown("---")
    
    # Create the main visualization
    fig = go.Figure()
    
    # Add loan balance line
    fig.add_trace(go.Scatter(
        x=df['Month'],
        y=df['Balance'],
        mode='lines',
        name='Loan Balance',
        line=dict(color='#FF6B6B', width=3),
        fill='tozeroy',
        fillcolor='rgba(255, 107, 107, 0.1)'
    ))
    
    # Add cumulative interest line
    df['Cumulative_Interest'] = df['Interest'].cumsum()
    fig.add_trace(go.Scatter(
        x=df['Month'],
        y=df['Cumulative_Interest'],
        mode='lines',
        name='Cumulative Interest',
        line=dict(color='#4ECDC4', width=2, dash='dash')
    ))
    
    # Add cumulative principal line
    df['Cumulative_Principal'] = df['Principal'].cumsum()
    fig.add_trace(go.Scatter(
        x=df['Month'],
        y=df['Cumulative_Principal'],
        mode='lines',
        name='Cumulative Principal',
        line=dict(color='#95E1D3', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title='Loan Balance Over Time',
        xaxis_title='Month',
        yaxis_title='Amount (€)',
        hovermode='x unified',
        height=500,
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Create payment breakdown chart
    st.subheader("Monthly Payment Breakdown")
    
    fig2 = go.Figure()
    
    fig2.add_trace(go.Bar(
        x=df['Month'],
        y=df['Principal'],
        name='Principal Payment',
        marker_color='#95E1D3'
    ))
    
    fig2.add_trace(go.Bar(
        x=df['Month'],
        y=df['Interest'],
        name='Interest Payment',
        marker_color='#4ECDC4'
    ))
    
    fig2.update_layout(
        barmode='stack',
        xaxis_title='Month',
        yaxis_title='Payment Amount (€)',
        height=400,
        template='plotly_white',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Display amortization table
    with st.expander("📋 View Complete Amortization Schedule"):
        # Format the dataframe for display
        display_df = df.copy()
        display_df['Payment'] = display_df['Payment'].apply(lambda x: f"€{x:,.2f}")
        display_df['Principal'] = display_df['Principal'].apply(lambda x: f"€{x:,.2f}")
        display_df['Interest'] = display_df['Interest'].apply(lambda x: f"€{x:,.2f}")
        display_df['Balance'] = display_df['Balance'].apply(lambda x: f"€{x:,.2f}")
        
        st.dataframe(display_df, use_container_width=True, height=400)

else:
    st.info("👆 Enter loan details above to see the amortization schedule.")

# ─────────────────────────────────────────────
# 🐍 Snake Game
# ─────────────────────────────────────────────
st.markdown("---")
st.subheader("🐍 Snake Game")
st.markdown("Use the arrow buttons below (or keyboard arrow keys) to control the snake. Eat the 🍎 to grow and score points!")

snake_html = """
<style>
  #snake-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    font-family: sans-serif;
  }
  #gameCanvas {
    border: 3px solid #4ECDC4;
    border-radius: 6px;
    background: #1a1a2e;
    display: block;
  }
  #score-bar {
    display: flex;
    gap: 40px;
    margin-bottom: 10px;
    font-size: 18px;
    font-weight: bold;
    color: #4ECDC4;
  }
  #message {
    margin-top: 8px;
    font-size: 16px;
    color: #FF6B6B;
    min-height: 24px;
  }
  .ctrl-grid {
    display: grid;
    grid-template-columns: repeat(3, 52px);
    grid-template-rows: repeat(2, 52px);
    gap: 6px;
    margin-top: 14px;
  }
  .ctrl-grid button {
    width: 52px;
    height: 52px;
    font-size: 22px;
    border: 2px solid #4ECDC4;
    border-radius: 8px;
    background: #16213e;
    color: #4ECDC4;
    cursor: pointer;
    transition: background 0.15s;
    user-select: none;
  }
  .ctrl-grid button:hover,
  .ctrl-grid button:active { background: #4ECDC4; color: #16213e; }
  #startBtn {
    margin-top: 16px;
    padding: 10px 32px;
    font-size: 16px;
    border: none;
    border-radius: 8px;
    background: #4ECDC4;
    color: #16213e;
    font-weight: bold;
    cursor: pointer;
  }
  #startBtn:hover { background: #95E1D3; }
</style>

<div id="snake-wrapper">
  <div id="score-bar">
    <span>Score: <span id="scoreVal">0</span></span>
    <span>High Score: <span id="highVal">0</span></span>
  </div>
  <canvas id="gameCanvas" width="420" height="420"></canvas>
  <div id="message">Press Start to play!</div>
  <div class="ctrl-grid">
    <span></span>
    <button ontouchstart="changeDir(0,-1)" onclick="changeDir(0,-1)">▲</button>
    <span></span>
    <button ontouchstart="changeDir(-1,0)" onclick="changeDir(-1,0)">◀</button>
    <button ontouchstart="changeDir(0,1)"  onclick="changeDir(0,1)">▼</button>
    <button ontouchstart="changeDir(1,0)"  onclick="changeDir(1,0)">▶</button>
  </div>
  <button id="startBtn" onclick="startGame()">▶ Start</button>
</div>

<script>
  const canvas = document.getElementById('gameCanvas');
  const ctx    = canvas.getContext('2d');
  const COLS = 21, ROWS = 21;
  const CELL = canvas.width / COLS;

  let snake, dir, nextDir, food, score, highScore = 0, gameLoop, running = false;

  function startGame() {
    snake   = [{x:10,y:10},{x:9,y:10},{x:8,y:10}];
    dir     = {x:1, y:0};
    nextDir = {x:1, y:0};
    score   = 0;
    running = true;
    document.getElementById('scoreVal').textContent = 0;
    document.getElementById('message').textContent  = '';
    placeFood();
    clearInterval(gameLoop);
    gameLoop = setInterval(tick, 130);
  }

  function placeFood() {
    let pos;
    do {
      pos = {x: Math.floor(Math.random()*COLS), y: Math.floor(Math.random()*ROWS)};
    } while (snake.some(s => s.x===pos.x && s.y===pos.y));
    food = pos;
  }

  function changeDir(dx, dy) {
    if (dx !== 0 && dir.x !== 0) return;
    if (dy !== 0 && dir.y !== 0) return;
    nextDir = {x: dx, y: dy};
  }

  function tick() {
    dir = nextDir;
    const head = {x: snake[0].x + dir.x, y: snake[0].y + dir.y};

    if (head.x < 0 || head.x >= COLS || head.y < 0 || head.y >= ROWS) { endGame(); return; }
    if (snake.some(s => s.x===head.x && s.y===head.y))                 { endGame(); return; }

    snake.unshift(head);

    if (head.x === food.x && head.y === food.y) {
      score++;
      document.getElementById('scoreVal').textContent = score;
      if (score > highScore) {
        highScore = score;
        document.getElementById('highVal').textContent = highScore;
      }
      placeFood();
    } else {
      snake.pop();
    }
    draw();
  }

  function endGame() {
    clearInterval(gameLoop);
    running = false;
    document.getElementById('message').textContent = '💀 Game Over! Press Start to retry.';
    draw();
  }

  function draw() {
    // Background
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Subtle grid
    ctx.fillStyle = 'rgba(255,255,255,0.04)';
    for (let r = 0; r < ROWS; r++)
      for (let c = 0; c < COLS; c++)
        ctx.fillRect(c*CELL + CELL/2 - 1, r*CELL + CELL/2 - 1, 2, 2);

    // Food
    ctx.font = `${Math.floor(CELL - 4)}px serif`;
    ctx.textAlign    = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('🍎', food.x*CELL + CELL/2, food.y*CELL + CELL/2 + 1);

    // Snake body
    snake.forEach((seg, i) => {
      const ratio = i / snake.length;
      ctx.fillStyle = i === 0
        ? '#4ECDC4'
        : `hsl(${170 + ratio*30}, 60%, ${55 - ratio*20}%)`;
      ctx.beginPath();
      ctx.roundRect(seg.x*CELL + 1, seg.y*CELL + 1, CELL - 2, CELL - 2, 5);
      ctx.fill();

      // Eyes on head
      if (i === 0) {
        ctx.fillStyle = '#1a1a2e';
        const isH = dir.x !== 0;
        const eye1 = isH
          ? {ex: seg.x*CELL + CELL*0.65, ey: seg.y*CELL + CELL*0.3}
          : {ex: seg.x*CELL + CELL*0.3,  ey: seg.y*CELL + CELL*0.65};
        const eye2 = isH
          ? {ex: seg.x*CELL + CELL*0.65, ey: seg.y*CELL + CELL*0.7}
          : {ex: seg.x*CELL + CELL*0.7,  ey: seg.y*CELL + CELL*0.65};
        [eye1, eye2].forEach(e => {
          ctx.beginPath();
          ctx.arc(e.ex, e.ey, 2.5, 0, Math.PI*2);
          ctx.fill();
        });
      }
    });
  }

  // Keyboard support — prevent page scroll on arrow keys
  document.addEventListener('keydown', e => {
    const map = {ArrowUp:[0,-1], ArrowDown:[0,1], ArrowLeft:[-1,0], ArrowRight:[1,0]};
    if (map[e.key]) { e.preventDefault(); changeDir(...map[e.key]); }
  });

  draw(); // idle splash
</script>
"""

st.components.v1.html(snake_html, height=780, scrolling=False)
