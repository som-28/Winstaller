# Winstaller

**Version:** 1.0.0

A modern, user-friendly GUI application for managing Windows software packages using Windows Package Manager (winget). Winstaller provides an intuitive interface to search, install, uninstall, and upgrade applications on Windows systems.

## 🚀 Features

### Current Features (v1.0.0)
- **Search Applications**: Search for available packages in the winget repository
- **Install Applications**: Silent installation with package agreement acceptance
- **View Installed Applications**: See all installed apps with their current versions
- **Uninstall Applications**: Remove installed applications with confirmation dialogs
- **Check for Updates**: View available updates for installed applications
- **Upgrade Applications**: Update existing applications to their latest versions
- **Progress Tracking**: Visual progress indicators during installation/uninstallation
- **Threaded Operations**: Non-blocking UI with background installation processes
- **Error Handling**: Proper error messages and user feedback
- **Tabbed Interface**: Organized interface with separate tabs for different functions

### User Interface
- Clean and intuitive PyQt5-based GUI with tabbed interface
- **Search & Install Tab**: Real-time search functionality and easy installation
- **Installed Apps Tab**: View all installed applications with versions
- Double-click to install applications from search results
- Double-click to uninstall applications from installed list
- Progress bars for installation/uninstallation status
- Success/error notifications
- Refresh and update checking capabilities

## 🛠️ Technical Stack

- **Frontend**: PyQt5 (GUI Framework)
- **Backend**: Python 3.x
- **Package Manager**: Windows Package Manager (winget)
- **Build Tool**: PyInstaller

## 📋 Requirements

### System Requirements
- Windows 10 version 1809 (17763) or later
- Windows Package Manager (winget) installed
- Python 3.7+ (for development)

### Python Dependencies
- PyQt5
- subprocess (built-in)
- os (built-in)

## 🔧 Installation & Setup

### For End Users (Using Pre-built Executable)
1. Download the latest release from the releases section
2. Extract the executable file
3. Run `main.exe` directly - no installation required!

### For Developers

#### Prerequisites
1. **Install Python 3.7+**
   ```powershell
   # Download from python.org or use winget
   winget install Python.Python.3
   ```

2. **Install winget** (if not already installed)
   ```powershell
   # Usually comes with Windows 10/11
   # Or install from Microsoft Store: "App Installer"
   ```

#### Setup Development Environment
1. **Clone or download the project**
   ```powershell
   git clone <your-repo-url>
   cd Winstaller
   ```

2. **Install Python dependencies**
   ```powershell
   pip install PyQt5
   ```

3. **Run the application**
   ```powershell
   python main.py
   ```

## 🏗️ Building from Source

### Building Executable with PyInstaller

1. **Install PyInstaller**
   ```powershell
   pip install pyinstaller
   ```

2. **Build the executable**
   ```powershell
   pyinstaller main.spec
   ```
   
   Or use the one-liner command:
   ```powershell
   pyinstaller --onefile --windowed --name=Winstaller main.py
   ```

3. **Find your executable**
   The built executable will be in the `dist/` folder.


## 📖 Usage Guide

### Basic Usage
1. **Launch Winstaller**
   - Run the executable or use `python main.py`

2. **Search & Install Applications (Search & Install Tab)**
   - Type the name of the software you want to install in the search box
   - Click "Search" or press Enter
   - Browse through the search results
   - Double-click on any application to install it
   - Confirm installation in the dialog box

3. **Manage Installed Applications (Installed Apps Tab)**
   - Switch to the "Installed Apps" tab
   - Click "Refresh Installed Apps" to see all installed applications and their versions
   - Click "Show Available Updates" to see which apps can be upgraded
   - Double-click on any installed application to uninstall it
   - Confirm uninstallation in the dialog box

4. **Monitor Progress**
   - Watch progress bars during installation/uninstallation
   - You'll see success/error messages when operations complete

### Advanced Features
- **Silent Installation**: All installations are performed silently with automatic package agreement acceptance
- **Background Processing**: Installations and uninstallations run in separate threads to keep the UI responsive
- **Version Tracking**: View current versions of all installed applications
- **Update Management**: Check for and view available updates for installed software
- **Confirmation Dialogs**: Safety prompts before uninstalling applications

## 🗂️ Project Structure

```
Winstaller/
├── main.py              # Application entry point
├── main_window.py       # Main window class
├── widgets.py           # Custom UI widgets (SearchWidget)
├── dialogs.py           # Dialog windows (InstallDialog)
├── winget_manager.py    # Winget operations manager
├── config_manager.py    # Configuration management
├── main.spec           # PyInstaller build configuration
├── build/              # Build artifacts (generated)
├── dist/               # Distribution files (generated)
└── __pycache__/        # Python cache files (generated)
```

## 🚧 Planned Features (Future Versions)

### Version 1.1.0
- [ ] **Batch Operations**: Install/uninstall multiple applications at once
- [ ] **Favorites System**: Save frequently used applications
- [ ] **Installation History**: Track installed applications and installation dates
- [ ] **Automatic Updates**: One-click update all available applications
- [ ] **Export/Import**: Export list of installed apps for backup/sharing

### Version 1.2.0
- [ ] **Dark/Light Theme Toggle**: Customizable UI themes
- [ ] **Advanced Filters**: Filter search results by category, publisher, etc.
- [ ] **Application Details**: Show detailed information about packages
- [ ] **Settings Panel**: Configurable installation options

### Version 1.3.0
- [ ] **Package Lists**: Import/export lists of applications
- [ ] **Scheduled Updates**: Automatic update checking
- [ ] **System Integration**: Add to Windows context menu
- [ ] **Logging System**: Detailed operation logs

### Version 2.0.0
- [ ] **Plugin System**: Support for additional package managers
- [ ] **Remote Management**: Manage applications on remote machines
- [ ] **Enterprise Features**: Group policies and deployment tools
- [ ] **Web Interface**: Optional web-based management portal

## 🐛 Troubleshooting

### Common Issues

**Application doesn't start**
- Ensure winget is installed and accessible from command line
- Check Windows version compatibility
- Verify all dependencies are installed

**Search returns no results**
- Check internet connection
- Verify winget is working: `winget search <app-name>` in PowerShell
- Try different search terms

**Installation fails**
- Run as administrator if needed
- Check if the application is already installed
- Verify sufficient disk space
- Check antivirus software settings

**Installed apps list is empty or incomplete**
- Ensure you have some applications installed via winget
- Try running `winget list` in PowerShell to verify winget can see installed apps
- Some applications installed outside of winget may not appear
- Click "Refresh Installed Apps" to reload the list

**Uninstallation fails**
- Run as administrator if needed
- Some applications may require manual uninstallation
- Check if the application is currently running and close it first
- Try uninstalling directly through Windows Settings if winget fails

### Getting Help
- Check the error messages in the application dialogs
- Verify winget functionality in PowerShell
- Ensure you have the latest version of Winstaller

## 🤝 Contributing

Contributions are welcome! Areas where you can help:

1. **Bug Reports**: Report issues and bugs
2. **Feature Requests**: Suggest new features
3. **Code Contributions**: Submit pull requests
4. **Documentation**: Improve documentation and guides
5. **Testing**: Test on different Windows versions

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Microsoft for Windows Package Manager (winget)
- Qt/PyQt5 development team
- Python community
- All contributors and testers

## 📞 Contact

For questions, suggestions, or support, please:
- Open an issue on GitHub
- Check the troubleshooting section above
- Review existing issues for similar problems

---

**Made with ❤️ for the Windows community**

*Last updated: July 29, 2025*
