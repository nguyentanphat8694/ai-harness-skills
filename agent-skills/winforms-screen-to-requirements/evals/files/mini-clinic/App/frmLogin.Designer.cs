partial class frmLogin
{
    private void InitializeComponent()
    {
        this.txtUser = new DevExpress.XtraEditors.TextEdit();
        this.txtPass = new DevExpress.XtraEditors.TextEdit();
        this.btnLogin = new DevExpress.XtraEditors.SimpleButton();
        this.lblUser.Text = "Tên đăng nhập";
        this.lblPass.Text = "Mật khẩu";
        this.btnLogin.Text = "ĐĂNG NHẬP";
        this.btnLogin.Click += new System.EventHandler(this.btnLogin_Click);
        this.Text = "ĐĂNG NHẬP";
    }
}
