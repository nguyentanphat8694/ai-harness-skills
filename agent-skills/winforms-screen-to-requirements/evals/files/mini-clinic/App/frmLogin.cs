using System;
using System.Windows.Forms;
namespace MiniClinic
{
    public partial class frmLogin : Form
    {
        private void btnLogin_Click(object sender, EventArgs e)
        {
            if (txtUser.Text == "" || txtPass.Text == "")
            {
                MessageBox.Show("Nhập tên đăng nhập và mật khẩu");
                return;
            }
            Session.CurrentUser = UserDal.Check(txtUser.Text, txtPass.Text);
            if (Session.CurrentUser == null) { MessageBox.Show("Sai tên đăng nhập hoặc mật khẩu"); return; }
            new frmMain().Show();
            this.Hide();
        }
    }
}
