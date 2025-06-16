def load_stylesheet():
    return """
    /* Main application styles */
    QMainWindow, QWidget {
        background: transparent;
        color: #ffffff;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    /* Main background */
    #mainBackground {
        background-color: #2C3E50;
        
    }
    
    /* Sidebar styles */
    #sidebar {
        background-color: #20202e;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    #sidebarLogo {
        color: #ffffff;
        font-size: 24px;
        font-weight: bold;
    }
    
    #sidebarButton {
        color: 	#E0E0E0;
        background-color: transparent;
        border: none;
        border-radius: 4px;
        padding: 8px;
        text-align: left;
        font-size: 14px;
        font-weight: bold; 
        
    }
    
    #sidebarButton:hover {
        color: #A785F5;
        background-color: rgba(255, 255, 255, 0.1);
        font-size:16px;font-weight: bold;
    }
    
    #sidebarButton:checked {
        color: #A785F5;
        background-color: rgba(147, 112, 219, 0.1);
        font-size:16px;font-weight: bold;
    }
    
    #subMenuButton {
        color: #CCCCCC;
        background-color: transparent;
        border: none;
        border-radius: 4px;
        padding: 5px;
        text-align: left;
        font-size: 12px;font-weight: 800;
    }
    
    #subMenuButton:hover {
        color: white;
        background-color: rgba(255, 255, 255, 0.1);font-size:15px;
        font-weight: 800;
    }
    
    #bulletPoint {
        color: #9370DB;
        font-size: 16px;
        font-weight: bold;
    }
    
    /* Header styles */
    #appTitle {
        color: white;         
        font-size: 20px;
        font-weight: bold;
    }
    
    #adminButton {
        color: #ffffff;
        font-size: 14px;
        padding: 6px 12px;
        background-color: #8E24AA;
        border-radius: 4px;font-weight: bold;
    }
    
    #adminButton:hover {
        background-color: #6A1B9A ;font-weight: bold;
    }
    
    #adminSidebarButton {
        color: #ffffff;
        font-weight: bold;
        
    }
    
    QToolButton::menu-indicator {
        width: 0px;
    }
    
    /* Content area styles */
    #contentWidget {
        border-image: url("assets/background.jpg") 0 0 0 0 stretch stretch; 
        
    }
    
    /* Dashboard card styles */
    #dashboardCard {
        background-color: rgba(40, 40, 60, 0.6);
        border-radius: 8px;
    }
    
    #cardTitle {
        color: white;
        font-size: 16px;
        font-weight: bold;
    }
    
    #cardValue {
        color: white;
        font-size: 28px;
        font-weight: bold;
    }
    
    /* Empty page placeholder */
    #emptyPageLabel {
        color:white;
        font-size: 18px;
        background:transparent;
    }
    """