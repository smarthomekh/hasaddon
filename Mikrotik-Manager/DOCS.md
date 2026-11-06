# MikroTik Manager
<p align="center">
  <img
    src="https://raw.githubusercontent.com/smarthomekh/hasaddon/Mikrotik-Manager/main/banner.png"
    alt="MikroTik Manager Logo" width="180"
  />
</p>
<p align="center">
  <strong>Smart Home Cambodia – Home Assistant Add-on</strong>
  <br>
  Manage, Monitor & Control Your MikroTik Network
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Home%20Assistant-Add--on-blue?logo=homeassistant" alt="Home Assistant Add-on">
  <img src="https://img.shields.io/badge/RouterOS-v7-blue?logo=mikrotik" alt="RouterOS v7">
  <img src="https://img.shields.io/badge/Version-1.4.16-green" alt="Version 1.4.16">
  <img src="https://img.shields.io/badge/Platform-ARM%20%7C%20x86-lightgrey" alt="Supported platforms">
</p>

---

## Overview

**MikroTik Manager** is a Home Assistant add-on developed by **Smart Home Cambodia** to manage and monitor MikroTik routers directly from your Home Assistant dashboard.

It provides a convenient web-based interface for managing network bandwidth, controlling internet access, scheduling device restrictions, managing firewall rules, filtering popular games and websites, and monitoring real-time network traffic.

Instead of accessing MikroTik RouterOS through WinBox or WebFig for everyday network management, you can manage important network functions from one centralized interface.

### Key Features

| Feature | Description |
|---|---|
| Simple Queues | Manage bandwidth limits for individual devices and IP addresses. |
| Speed Management | Control upload and download bandwidth. |
| Multi-Restriction Scheduler | Create multiple independent internet access schedules for devices. |
| Game Blocking | Block popular online games with one-click controls. |
| Website Filtering | Restrict websites and social media platforms. |
| Firewall Controls | Block or restore internet access for individual devices. |
| Live Network Monitoring | Monitor real-time WAN and LAN throughput. |
| RouterOS REST API | Communicate directly with MikroTik RouterOS v7. |
| Home Assistant Ingress | Access the management interface securely through Home Assistant authentication. |

### Supported Game Filtering

The add-on includes predefined blocking options for:

- Roblox
- Minecraft
- Fortnite
- Free Fire
- PUBG
- Steam
- Mobile Legends

### Supported Website & Social Media Filtering

Predefined filtering options include:

- TikTok
- YouTube
- Instagram
- Discord
- Facebook
- Reddit
- Custom domains

Filtering behavior depends on the RouterOS firewall and DNS configuration.

---

## Requirements

Before installing MikroTik Manager, ensure you have:

- Home Assistant with Add-on Store support.
- A MikroTik router running RouterOS v7.
- RouterOS REST API enabled.
- Network connectivity between Home Assistant and the MikroTik router.
- A dedicated RouterOS user account with appropriate permissions.

### Supported Architectures

The add-on configuration currently declares support for:

- aarch64
- amd64
- armv7
- armhf
- i386

---

## Installation

### Method 1 – Home Assistant Add-on Repository

**Step 1 – Add the repository**

1. Open Home Assistant.
2. Navigate to **Settings → Add-ons → Add-on Store**.
3. Click the three-dot menu in the upper-right corner.
4. Select **Repositories**.
5. Add this repository:

```text
https://github.com/smarthomekh/hasaddon
```

6. Click **Add**.

**Step 2 – Install MikroTik Manager**

1. Return to the Add-on Store.
2. Find **MikroTik Manager**.
3. Open the add-on information page.
4. Click **Install**.
5. Wait for the installation to complete.

**Step 3 – Configure the add-on**

Open the Configuration tab and enter your MikroTik router connection details.

**Step 4 – Start the add-on**

1. Click **Save**.
2. Open the Info tab.
3. Click **Start**.
4. Enable **Show in sidebar**.

You can now access MikroTik Manager directly from the Home Assistant sidebar.

---

## RouterOS Configuration

MikroTik Manager communicates with RouterOS using the REST API.

RouterOS v7 provides REST API access through the WebFig HTTP or HTTPS service.

### Step 1 – Enable the REST API service

For HTTPS (recommended):

```routeros
/ip service enable www-ssl
```

For HTTP (testing only):

```routeros
/ip service enable www
```

Default ports:

| Service | Port | Security |
|---|---:|---|
| www | 80 | HTTP |
| www-ssl | 443 | HTTPS |

### Step 2 – Create a dedicated RouterOS user

For better security, create a separate account for MikroTik Manager instead of using your primary administrator account.

Run the following commands in MikroTik Terminal:

```routeros
/user group add name=ha-manager policy=read,write,api,rest-api,test,policy,sensitive

/user add name=ha-manager group=ha-manager password=YOUR_STRONG_PASSWORD
```

Replace `YOUR_STRONG_PASSWORD` with your own strong password.

The permissions above are based on the current project setup. Some features may require additional permissions depending on your RouterOS configuration.

### Step 3 – Restrict management access

For improved security, restrict the REST API service to trusted network addresses.

For example:

```routeros
/ip service set www-ssl address=192.168.100.0/24
```

Replace the example network with your actual Home Assistant management network.

Avoid exposing RouterOS management services directly to the public internet.

---

## Add-on Configuration

Open:

**Home Assistant → Settings → Add-ons → MikroTik Manager → Configuration**

The following options are available in the current add-on configuration.

| Option | Default | Description |
|---|---|---|
| router_host | 192.168.88.1 | MikroTik router IP address or hostname. |
| router_port | 80 | RouterOS REST API service port. |
| router_user | admin | RouterOS username. |
| router_password | Empty | RouterOS password. |
| use_ssl | false | Enable HTTPS communication. |
| allow_insecure_cert | true | Allow certificates that cannot be verified. |
| poll_interval | 1000 | Interface polling interval in milliseconds. |

### Recommended HTTPS Configuration

For production environments, use HTTPS with a valid router certificate.

Example:

```yaml
router_host: 192.168.100.1
router_port: 443
router_user: ha-manager
router_password: YOUR_STRONG_PASSWORD
use_ssl: true
allow_insecure_cert: false
poll_interval: 1000
```

Adjust the router address to match your network.

**Important:** If your router uses a self-signed certificate, certificate verification may need to be temporarily relaxed. For production use, configure a trusted certificate and disable insecure certificate acceptance.

---

## Managing Your Network

### 1. Bandwidth Management

Use Simple Queues to control internet bandwidth for individual devices or IP addresses.

Typical use cases:

- Limit bandwidth for individual users.
- Control download and upload speeds.
- Prevent one device from consuming all available bandwidth.
- Manage bandwidth for specific IP addresses.

### 2. Internet Access Scheduling

The Multi-Restriction Scheduler allows you to configure multiple independent restriction periods for individual devices.

Example use cases:

- Restrict internet access during study hours.
- Schedule internet access for children.
- Limit internet usage during nighttime.
- Configure multiple access-control windows.

### 3. Game Blocking

Use predefined game-blocking controls to restrict access to popular online games.

Supported options include Roblox, Minecraft, Fortnite, Free Fire, PUBG, Steam, and Mobile Legends.

### 4. Website & Social Media Filtering

Manage website access using predefined filtering options and custom domains.

Examples include TikTok, YouTube, Instagram, Facebook, Discord, and Reddit.

### 5. Firewall Controls

Manage device internet access through RouterOS firewall and address-list rules.

Typical operations include:

- Block a device from accessing the internet.
- Restore internet access.
- Manage device restriction rules.

### 6. Real-Time Network Monitoring

Monitor network throughput through live charts and gauges.

Available monitoring categories include:

- WAN throughput.
- LAN throughput.
- Network traffic activity.

---

## Security & Privacy

MikroTik Manager is designed to communicate with your router through the RouterOS REST API.

Please follow these security recommendations:

1. Use a dedicated RouterOS management account.
2. Use HTTPS instead of HTTP whenever possible.
3. Use a valid TLS certificate.
4. Restrict REST API access to trusted network addresses.
5. Never expose the management interface directly to the public internet.
6. Use strong router passwords.
7. Keep Home Assistant, RouterOS, and the add-on updated.
8. Back up your MikroTik configuration before making major changes.

**Authentication:** When installed through Home Assistant, the web interface uses Home Assistant Ingress authentication and does not implement a separate login system.

If deploying the standalone Docker version, port 3000 must be protected by a trusted LAN or an authenticated reverse proxy. Anyone who can access an unprotected standalone interface may be able to control your router.

The router password is stored in `/data/config.json` inside the add-on's private data volume.

---

## Troubleshooting

### Cannot connect to MikroTik router

Check the following:

- Verify the router IP address.
- Verify the configured port.
- Ensure the REST API service is enabled.
- Confirm that Home Assistant can reach the router.
- Verify your username and password.
- Check the RouterOS user permissions.

### HTTPS certificate error

If you encounter a certificate verification error:

- Check whether the router has a valid certificate.
- Verify that the certificate matches the router hostname.
- Ensure the certificate is trusted by the add-on.
- Only temporarily enable insecure certificate acceptance when necessary.

### Add-on starts but cannot access the router

Check:

- RouterOS firewall rules.
- IP service access restrictions.
- Network routing between Home Assistant and MikroTik.
- RouterOS REST API service status.

### Network filtering does not work as expected

Check the relevant RouterOS firewall rules, DNS configuration, and address lists.

Some applications use encrypted DNS, dynamic IP addresses, or alternative network protocols, so domain-based filtering may not block every connection.

### Live monitoring is unavailable

Check the router connection and the configured polling interval. Review the add-on logs for errors.

---

## Frequently Asked Questions

**Q: Does MikroTik Manager support RouterOS v6?**

A: The current project documentation targets RouterOS v7 and its REST API. RouterOS v6 is not a supported target.

**Q: Can I manage multiple MikroTik routers?**

A: The current add-on configuration defines one router connection. Multiple-router management is not documented as a supported feature.

**Q: Does it require the MikroTik API service on port 8728?**

A: No. This add-on uses the RouterOS REST API through the `www` or `www-ssl` service, not the traditional RouterOS API service.

**Q: Can I access MikroTik Manager outside my home network?**

A: Yes, through an appropriately secured remote-access setup for Home Assistant, such as a secure VPN or authenticated remote-access solution.

**Q: Is it compatible with Home Assistant Ingress?**

A: Yes. Home Assistant Ingress is enabled in the current add-on configuration.

---

## Development

To run the application locally:

```bash
npm install
npm run dev
```

The development server is available at:

```text
http://localhost:3000
```

To build the application:

```bash
npm run build
```

---

## Support & Feedback

If you encounter an issue, have a suggestion, or want to request a new feature, please open an issue.

- **GitHub Repository:** https://github.com/smarthomekh/hasaddon
- **Bug Reports:** https://github.com/smarthomekh/hasaddon/issues
- **Smart Home Cambodia:** https://smarthomekh.com

When submitting a bug report, please include:

- MikroTik router model.
- RouterOS version.
- Home Assistant version.
- MikroTik Manager version.
- Error messages or add-on logs.
- Steps to reproduce the problem.

Do not include passwords, API credentials, or other sensitive information.

---

## Credits & License

**Developed and maintained by Smart Home Cambodia.**

Website: https://smarthomekh.com

GitHub: https://github.com/smarthomekh

MikroTik Manager is an independent community project and is not an official MikroTik product.

Home Assistant is a trademark of its respective owner. MikroTik is a trademark of MikroTikls SIA.

---

<p align="center">
  <strong>Smart Home Cambodia</strong>
  <br>
  Modern Life with Automation
  <br><br>
  Built for the Home Assistant Community.
</p>
