# VPN Browser Agent

A powerful browser automation agent that maintains persistent VPN connections across sessions. Perfect for web scraping, automation, and privacy-focused browsing tasks.

## 🎯 Features

- **Persistent VPN Sessions**: VPN connections persist across browser sessions
- **Multiple VPN Support**: Browser extensions and system-level VPN
- **Automatic Connection**: Auto-connect to VPN services
- **IP Verification**: Check VPN status and IP changes
- **Flexible Configuration**: Easy setup for popular VPN services
- **Manual Override**: Fallback to manual VPN setup when needed

## 🏗️ Architecture

```
vpn_browser_agent/
├── vpn_browser_agent.py      # Main VPN browser agent
├── vpn_config.py             # VPN extension configuration
├── test_vpn_agent.py         # Test suite
├── vpn_extensions/           # VPN extension storage
├── vpn_browser_session/      # Persistent browser session
└── .env                      # Environment configuration
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
playwright install
```

### 2. Setup VPN Extension (Optional)
```bash
# List available VPN extensions
python vpn_config.py list

# Setup a specific VPN extension
python vpn_config.py setup nordvpn
```

### 3. Configure Environment
Create or update your `.env` file:
```bash
# For browser extension VPN
VPN_EXTENSION_PATH=./vpn_extensions/nordvpn
VPN_EXTENSION_ID=your_extension_id
USE_SYSTEM_VPN=false

# For system-level VPN (macOS)
USE_SYSTEM_VPN=true
VPN_SERVICE_NAME=YourVPNServiceName
```

### 4. Test the Agent
```bash
python test_vpn_agent.py
```

### 5. Use in Your Code
```python
from vpn_browser_agent import VPNBrowserAgent

# Create agent
agent = VPNBrowserAgent(headless=False)

# Launch browser with VPN
agent.launch_browser_with_vpn()

# Connect VPN
agent.connect_vpn_extension()

# Check status
ip = agent.check_vpn_status()
print(f"Current IP: {ip}")

# Navigate with VPN active
agent.navigate_to("https://example.com")

# Keep session alive
agent.keep_alive()
```

## 🔧 VPN Extension Setup

### Supported VPN Services
- **NordVPN** - `python vpn_config.py setup nordvpn`
- **ExpressVPN** - `python vpn_config.py setup expressvpn`
- **ProtonVPN** - `python vpn_config.py setup protonvpn`
- **Windscribe** - `python vpn_config.py setup windscribe`

### Manual Extension Setup
1. Download VPN extension from Chrome Web Store
2. Extract the `.crx` file to `vpn_extensions/<service_name>/`
3. Extract extension ID from `manifest.json`
4. Update `.env` file with path and ID

### Extension ID Extraction
```bash
python vpn_config.py extract ./vpn_extensions/nordvpn
```

## 🔒 VPN Connection Methods

### 1. Browser Extension VPN (Recommended)
- **Pros**: Granular control, persistent across sessions
- **Cons**: Requires extension setup
- **Best for**: Web automation, privacy browsing

### 2. System-Level VPN
- **Pros**: Simple setup, affects all traffic
- **Cons**: Less granular control
- **Best for**: System-wide privacy, simple use cases

### 3. Manual VPN Setup
- **Pros**: Maximum flexibility
- **Cons**: Requires manual intervention
- **Best for**: Complex VPN configurations

## 📋 API Reference

### VPNBrowserAgent Class

#### Constructor
```python
VPNBrowserAgent(user_data_dir="vpn_browser_session", headless=False)
```

#### Methods

##### `launch_browser_with_vpn()`
Launch browser with VPN extension support.
```python
success = agent.launch_browser_with_vpn()
```

##### `connect_vpn_extension(auto_connect=True)`
Connect to VPN using browser extension.
```python
success = agent.connect_vpn_extension(auto_connect=True)
```

##### `connect_system_vpn()`
Connect to system-level VPN (macOS).
```python
success = agent.connect_system_vpn()
```

##### `check_vpn_status()`
Check current VPN connection status.
```python
ip_address = agent.check_vpn_status()
```

##### `navigate_to(url)`
Navigate to URL with VPN active.
```python
success = agent.navigate_to("https://example.com")
```

##### `wait_for_manual_setup()`
Wait for manual VPN setup.
```python
agent.wait_for_manual_setup()
```

##### `keep_alive()`
Keep browser session alive for inspection.
```python
agent.keep_alive()
```

##### `close()`
Close browser session and cleanup.
```python
agent.close()
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VPN_EXTENSION_PATH` | Path to VPN extension directory | `./vpn_extensions/nordvpn` |
| `VPN_EXTENSION_ID` | VPN extension ID | `fjoaledfpmneenckfbpohebmkfildcfl` |
| `USE_SYSTEM_VPN` | Use system-level VPN | `true` or `false` |
| `VPN_SERVICE_NAME` | System VPN service name | `NordVPN` |

### Browser Arguments
The agent automatically configures browser arguments for VPN support:
- `--load-extension`: Load VPN extension
- `--disable-extensions-except`: Only allow VPN extension
- `--disable-web-security`: Allow insecure content
- `--no-sandbox`: Disable sandbox for automation

## 🧪 Testing

### Run Full Test Suite
```bash
python test_vpn_agent.py
```

### Test Specific Components
```bash
# Test extension setup
python vpn_config.py list
python vpn_config.py setup nordvpn

# Test extension ID extraction
python vpn_config.py extract ./vpn_extensions/nordvpn
```

### Test Scenarios
1. **Browser Launch**: Verify browser starts with VPN support
2. **Extension Loading**: Check VPN extension loads correctly
3. **VPN Connection**: Test automatic VPN connection
4. **IP Verification**: Verify IP address changes
5. **Navigation**: Test browsing with VPN active
6. **Session Persistence**: Verify VPN persists across sessions

## 🔍 Troubleshooting

### Common Issues

#### VPN Extension Not Loading
```bash
# Check extension path
ls -la vpn_extensions/

# Verify extension ID
python vpn_config.py extract ./vpn_extensions/your_extension

# Check manifest.json
cat vpn_extensions/your_extension/manifest.json
```

#### Browser Launch Fails
```bash
# Install Playwright browsers
playwright install

# Check permissions
chmod +x vpn_browser_agent.py

# Run with debug
DEBUG=pw:api python test_vpn_agent.py
```

#### VPN Connection Fails
```bash
# Try manual setup
agent.wait_for_manual_setup()

# Check VPN service status
# Verify credentials and subscription
```

### Debug Mode
```bash
# Enable Playwright debug
DEBUG=pw:api python test_vpn_agent.py

# Enable verbose logging
python -v test_vpn_agent.py
```

## 🔐 Security Considerations

### Best Practices
1. **Use HTTPS**: Always navigate to HTTPS sites
2. **Verify VPN**: Check IP address before sensitive operations
3. **Session Isolation**: Use separate sessions for different tasks
4. **Credential Management**: Store VPN credentials securely
5. **Regular Updates**: Keep VPN extensions updated

### Privacy Features
- **IP Masking**: VPN hides real IP address
- **Traffic Encryption**: All traffic encrypted through VPN
- **Session Persistence**: VPN settings saved between sessions
- **No Logging**: Agent doesn't log sensitive data

## 🚀 Advanced Usage

### Custom VPN Extension
```python
# Load custom VPN extension
agent = VPNBrowserAgent()
agent.vpn_extension_path = "./custom_vpn_extension"
agent.vpn_extension_id = "custom_extension_id"
agent.launch_browser_with_vpn()
```

### Multiple VPN Services
```python
# Switch between VPN services
agent.connect_vpn_extension()  # Connect to primary VPN
# ... do work ...
agent.disconnect_vpn_extension()
agent.connect_system_vpn()     # Switch to system VPN
```

### Integration with Other Agents
```python
# Use with image generation agent
from vpn_browser_agent import VPNBrowserAgent
from chatgpt_image_gen import batch_generate_images_via_whatsapp

# Launch VPN browser
vpn_agent = VPNBrowserAgent()
vpn_agent.launch_browser_with_vpn()
vpn_agent.connect_vpn_extension()

# Use VPN browser for image generation
# (Modify chatgpt_image_gen.py to use existing browser context)
```

## 📝 Examples

### Basic VPN Browser Session
```python
from vpn_browser_agent import VPNBrowserAgent

agent = VPNBrowserAgent()
agent.launch_browser_with_vpn()
agent.connect_vpn_extension()
agent.navigate_to("https://whatismyipaddress.com/")
agent.keep_alive()
```

### Automated VPN Testing
```python
def test_vpn_connection():
    agent = VPNBrowserAgent()
    agent.launch_browser_with_vpn()
    
    # Check initial IP
    initial_ip = agent.check_vpn_status()
    
    # Connect VPN
    agent.connect_vpn_extension()
    
    # Check new IP
    vpn_ip = agent.check_vpn_status()
    
    if initial_ip != vpn_ip:
        print("✅ VPN connection successful!")
    else:
        print("❌ VPN connection failed")
    
    agent.close()
```

### Persistent VPN Session
```python
def create_persistent_vpn_session():
    agent = VPNBrowserAgent(user_data_dir="my_vpn_session")
    agent.launch_browser_with_vpn()
    agent.connect_vpn_extension()
    
    # Session will persist in my_vpn_session directory
    # Next time you use the same user_data_dir, VPN will be connected
    agent.keep_alive()
```

## 🤝 Contributing

### Adding New VPN Services
1. Add service info to `vpn_config.py`
2. Test extension loading and connection
3. Update documentation
4. Add to test suite

### Bug Reports
1. Check troubleshooting section
2. Run with debug mode
3. Provide error logs and system info
4. Include VPN service and version

## 📄 License

This project is open source. Feel free to use and modify for your needs.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the test suite
3. Check VPN service documentation
4. Verify environment configuration

---

**Happy browsing with VPN! 🔒🌐** 