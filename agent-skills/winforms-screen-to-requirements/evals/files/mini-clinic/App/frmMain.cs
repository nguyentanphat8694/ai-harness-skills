using System;
namespace MiniClinic
{
    public partial class frmMain : DevExpress.XtraBars.Ribbon.RibbonForm
    {
        frmReceipt receipt = null;
        void OpenReceipt()
        {
            if (receipt == null)
            {
                receipt = new frmReceipt();
                receipt.FormClosed += (s, e) => receipt = null;
                receipt.Show();
            }
            else receipt.Activate();
        }
        private void btnReceipt_ItemClick(object sender, ItemClickEventArgs e) { OpenReceipt(); }
        private void btnDrug_ItemClick(object sender, ItemClickEventArgs e) { new frmDrug().ShowDialog(); }
        private void btnTax_ItemClick(object sender, ItemClickEventArgs e) { new frmTaxReport().ShowDialog(); }
    }
}
