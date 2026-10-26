using System;
using System.Windows.Forms;
namespace MiniClinic
{
    static class Program
    {
        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.Run(new frmLogin());
        }
    }
}
