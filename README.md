# 🏦 Project: Real-Time ATM Monitoring System

## The problem we're solving

Imagine a bank has hundreds or thousands of ATMs.  
The bank wants to know in real time:

* Is an ATM online?
* Did an ATM go offline?
* Is an ATM running out of cash?
* Are there network/hardware problems?
* Are transactions suddenly failing?
* Is there unusual transaction activity?
* Which ATM needs attention right now, rather than after someone checks a report?
---
* We're building:
* ATM Event
* ↓
* Kafka
* ↓
* Real-Time Processing
* ↓
* Detect Important Situations
* ↓
* Alert
---

# 📡 Data Simulation & Event Generation

Before connecting the system to Apache Kafka, we first need a realistic source of continuous **ATM** events.

Since we do not have access to a real bank's live **ATM** infrastructure, we build a **simulation layer** that behaves like an **ATM** network generating events in real time.

The simulator does not simply generate random **JSON**.

It models:

- **ATM** machines
- Customer transactions
- **ATM** operational health
- Shared **ATM** state
- State-dependent events
- Continuous event generation

The objective is to create a realistic event stream that can later be connected to Kafka.

---

# 1. 🏧 ATM Machine Data

We first define the **ATM** network that our simulator represents.

For the initial version, we simulate **10 ATMs** distributed across different locations.

```text ATM_001 → Hyderabad ATM_002 → Delhi ATM_003 → Mumbai ATM_004 → Bangalore ATM_005 → Chennai ATM_006 → Pune ATM_007 → Kolkata ATM_008 → Ahmedabad ATM_009 → Jaipur ATM_010 → Kochi ```

Each **ATM** has information that describes its current state.

Example:

```json
{
    *atm_id*: *ATM_001*,
    *location*: *Hyderabad*,
    *cash_level*: **450000**,
    *status*: *ONLINE*
}
```

### ATM attributes

| Attribute    | Description                          |
| ------------ | ------------------------------------ |
| `atm_id`     | Unique identifier of the ATM         |
| `location`   | Physical location of the ATM         |
| `cash_level` | Current amount of cash available     |
| `status`     | Current operational state of the ATM |

The **ATM** information acts as the **base state of our simulated **ATM** network**.

---

# 2. 🔄 Two Types of Events

An **ATM** produces different kinds of events.

Instead of mixing everything into one event stream and one schema, we divide events into two logical domains.

```text
    **ATM** **NETWORK**
    │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
    Customer Activity       Machine Activity
    │                     │
    ▼                     ▼
    Transaction Events        Health Events
```

---

## 2.1 💳 Transaction Events

Transaction events represent **customer activity involving the **ATM****.

We currently simulate five transaction types:

```text **WITHDRAWAL** **DEPOSIT** BALANCE_CHECK FAILED_TRANSACTION CARD_RETAINED ```

Example:

```json
{
    *event_id*: *evt_a82f91cd*,
    *timestamp*: ***2026**-09-**16T20**:10:01*,
    *atm_id*: *ATM_001*,
    *location*: *Hyderabad*,
    *transaction_type*: *WITHDRAWAL*,
    *transaction_id*: *txn_72ab81cd*,
    *amount*: **5000**,
    *card_type*: *DEBIT*,
    *status*: *SUCCESS*
}
```

These events answer questions such as:

- How many transactions are happening?
- How much money is being withdrawn?
- Which **ATM** has the most transactions?
- How many transactions are failing?
- Are unusual transaction patterns occurring?

---

## 2.2 🖥️ ATM Health Events

Health events represent the **operational condition of the **ATM** itself**.

We currently simulate six health events:

```text ATM_ONLINE ATM_OFFLINE CASH_LOW CASH_REFILLED HARDWARE_ERROR NETWORK_ERROR ```

Example:

```json
{
    *event_id*: *health_72bc91*,
    *timestamp*: ***2026**-09-**16T20**:10:02*,
    *atm_id*: *ATM_001*,
    *location*: *Hyderabad*,
    *event_type*: *NETWORK_ERROR*,
    *cash_level*: **450000**,
    *status*: *ERROR*,
    *error_code*: *CONNECTION_LOST*
}
```

These events allow us to monitor:

- **ATM** availability
- Cash levels
- Network problems
- Hardware failures
- **ATM** recovery
- Operational incidents

---

# 3. 🗂️ Shared ATM Data

Both event generators operate on the **same **ATM** network**.

Instead of defining **ATM** information separately inside each generator, we maintain it in a common module:

```text atm_data.py ```

Architecture:

```text
    atm_data.py
    │
    Shared **ATM** Data
    │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
 Transaction Generator       Health Generator
```

This creates a **single source of truth**.

For example, if:

```text ATM_001 location = Hyderabad ```

then both generators use:

```text ATM_001 → Hyderabad ```

We avoid inconsistent situations such as:

```text Transaction Generator: ATM_001 → Hyderabad

Health Generator: ATM_001 → Delhi ```

The same principle applies to **ATM** state.

Both transaction and health events should refer to the same underlying **ATM**.

---

# 4. 🧠 State-Aware Simulation

A simple random event generator would produce events independently.

For example:

```text ATM_001 → **WITHDRAWAL** ₹5,**000** ATM_001 → ATM_OFFLINE ATM_001 → **WITHDRAWAL** ₹10,**000** ATM_001 → ATM_OFFLINE ```

This is problematic because the simulator doesn't understand the relationship between events.

If the **ATM** is offline, a successful withdrawal should not normally happen.

Therefore, our simulator is designed to be **state-aware**.

---

## What is ATM state?

Each **ATM** maintains a current state.

For example:

```json
{
    *atm_id*: *ATM_001*,
    *location*: *Hyderabad*,
    *cash_level*: **450000**,
    *status*: *ONLINE*
}
```

The state can change as events occur.

### Example: Withdrawal

Initial state:

```text ATM_001 cash_level = ₹**450**,**000** status = **ONLINE** ```

Customer withdraws ₹5,**000**:

```text
**WITHDRAWAL** ₹5,**000**
        ↓
cash_level = ₹**445**,**000**
```

Another withdrawal:

```text
**WITHDRAWAL** ₹10,**000**
        ↓
cash_level = ₹**435**,**000**
```

The simulator therefore maintains a relationship between:

```text Event ↓ ### State Change ```

---

## Example: ATM failure

Initial:

```text ATM_003 status = **ONLINE** ```

A network error occurs:

```text
NETWORK_ERROR
        ↓
status = **OFFLINE**
```

While the **ATM** is offline, the simulator should not generate normal successful transactions for that **ATM**.

When the **ATM** recovers:

```text
ATM_ONLINE
     ↓
status = **ONLINE**
```

Normal transactions can resume.

---

## Example: Cash monitoring

Suppose:

```text ATM_005 cash_level = ₹25,**000** ```

A withdrawal occurs:

```text
**WITHDRAWAL** ₹10,**000**
        ↓
cash_level = ₹15,**000**
```

Our configured threshold might be:

```text ₹20,**000** ```

Therefore:

```text
cash_level < threshold
        ↓
CASH_LOW
        ↓
⚠️ **ATM** requires replenishment
```

This creates realistic relationships between events instead of unrelated random data.

---

# Why are we making the simulator state-aware?

Because the purpose is not to generate large amounts of random data.

The purpose is to generate **meaningful streaming data that resembles a real **ATM** system**.

A state-aware simulator gives us:

```text Event ↓ ### State Change ↓ ### New State ↓ ### Possible Future Event ```

This becomes especially important when we later implement real-time processing.

For example, the processing layer can detect:

```text cash_level < threshold ```

or:

```text **ATM** status = **OFFLINE** ```

or:

```text failed transactions > threshold within a time window ```

The quality of our real-time processing depends heavily on the quality of the simulated events.

---

# 5. 🎛️ Orchestrator

We have two separate generators:

```text transaction_generator.py health_generator.py ```

They contain different event-generation logic.

However, we also need a component that coordinates the simulation.

That component is:

```text simulator.py ```

The orchestrator is responsible for:

- Maintaining the shared **ATM** state.
- Running transaction and health event generation.
- Ensuring both generators operate on the same **ATM** network.
- Coordinating the continuous simulation.
- Producing logically consistent events.

The architecture becomes:

```text
    simulator.py
    │
    Shared **ATM** State
    │
    ┌────────────┴────────────┐
    │                         │
    ▼                         ▼
    transaction_generator.py    health_generator.py
    │                         │
    ▼                         ▼
    Transaction Events             Health Events
```

The generators remain logically separate, while the orchestrator coordinates the overall simulation.

---

# 🏗️ Complete Data Simulation Architecture

```text
    **ATM** **NETWORK**
    │
    **ATM** Master Data
    │
    atm_data.py
    │
    ▼
    ┌─────────────────┐
    │  **ATM** **STATE**      │
    │                 │
    │ **ATM** ID          │
    │ Location        │
    │ Cash Level      │
    │ Status          │
    └────────┬────────┘
    │
    simulator.py
    **ORCHESTRATOR**
    │
    ┌────────────┴────────────┐
    │                         │
    ▼                         ▼
    **TRANSACTION** **GENERATOR**       **HEALTH** **GENERATOR**
    │                         │
    │                         │
    Customer Activity          Machine Activity
    │                         │
    ▼                         ▼
    ┌──────────────────┐      ┌──────────────────┐
    │ Transaction      │      │ Health           │
    │ Events           │      │ Events           │
    │                  │      │                  │
    │ Withdrawal       │      │ **ATM** Online       │
    │ Deposit          │      │ **ATM** Offline      │
    │ Balance Check    │      │ Cash Low         │
    │ Failed Tx        │      │ Cash Refilled    │
    │ Card Retained    │      │ Hardware Error   │
    └────────┬─────────┘      │ Network Error    │
    │                └────────┬─────────┘
    │                         │
    └────────────┬────────────┘
    │
    ▼
    **CONTINUOUS** **EVENTS**
    │
    ▼
    ┌───────────────┐
    │     **KAFKA**     │
    │               │
    │ atm-          │
    │ transactions  │
    │               │
    │ atm-health    │
    └───────────────┘
```

---

# 🔑 Design Summary

The simulation layer follows five important design decisions:

### 1. ATM Machine Data

We simulate a network of **10 ATMs**, each with its own identity, location, cash level and operational status.

### 2. Two Event Domains

We separate:

```text Transaction Events → Customer activity

Health Events → **ATM** operational activity ```

This keeps the event schemas clean and allows independent processing.

### 3. Shared ATM Data

Both generators use the same **ATM** information and state.

```text
    Shared **ATM** State
    │
    ┌─────────┴─────────┐
    ▼                   ▼
    Transactions            Health
```

This prevents inconsistent data.

### 4. State-Aware Simulation

Events can change **ATM** state.

```text
**WITHDRAWAL**
    ↓
Cash decreases

NETWORK_ERROR
    ↓
**ATM** becomes unavailable

ATM_ONLINE
    ↓
**ATM** becomes available

CASH_REFILLED
    ↓
Cash increases
```

This produces meaningful event relationships rather than completely random events.

### 5. Orchestrator

`simulator.py` coordinates the two generators and the shared state.

The result is one simulated **ATM** network producing two independent event streams.

---

# 📁 Data Simulation Components

```text
data_generator/
│
├── atm_data.py
│       └── Shared **ATM** master/state data
│
├── transaction_generator.py
│       └── Generates customer transaction events
│
├── health_generator.py
│       └── Generates **ATM** operational events
│
└── simulator.py
        └── Orchestrates the simulation
```

---