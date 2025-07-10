---
marp: true
theme: gaia
paginate: true
---
# FC-VPN  
## Cloud-Native Elastic VPN Solution

<br>

**Liu Yafei**  
**Qin Sihan**  
**Zhang Runze**  
**Zhang zeshen**

<br>
<small>July 2025</small>

---
# Problem Statement
| Traditional Solutions | Cloud-based Solutions |
|:--------------------- |:---------------------|
| - Fixed, inflexible capacity  <br> - Billing: fixed number of nodes  <br> - Poor at handling traffic spikes  <br> - Designed for large enterprises only <br>  | - Elastic scaling on demand  <br> - Instances created as needed  <br> - Pay-per-use billing  <br> - Flexible deployment for small businesses/teams <br>- auto-scaliing <br>|

---

# Implementation Principle  
<small>(Internal technical discussion only)</small>

- **VPN prototype:** Proxy forwards traffic (HTTPS over SOCKS5)
- **Elastic scaling:** Managed by Kubernetes (k8s)
- **User scaling:** Each proxy handles a fixed number of users; 
k8s auto-scales pods as amount of users changes

---

# Flowchart  
<small>(Internal technical discussion only)</small>

```mermaid
  A[User] --> B[Cloud VPN Proxy]
  B --> C[k8s Operator (Manages Pods)]
  C --> D[Each Pod Connects to Target Server]
  [draw on the broad, maybe]
```

---

# Assumptions  
<small>(Internal technical discussion only)</small>

- Pool of public IPs; each pod can be assigned a public IP to connect the Internet
- Target users (two directions): 
-1. small businesses/teams (NAT traverselNetwork Address Translation traversal)
-2. Bypassing the firewall
- Complete VPN component is available (instead the prototype)

---

# Demo

**Client (Frontend):**
- Multiple clients, each with a personal user profile (StatefulSet)
- Display outgoing public IP (optional, or as an element to show different IP by proxy)

**Proxy Monitor:**
- Real-time traffic monitoring
- Dynamic pod/node/objects count&details (via k8s dashboard, e.g. AWS)

---

# Discussion Questions

- The key technical challenges?
- Divide the work?
- Regarding "direction": good to see two or just focus on one?

  

---
