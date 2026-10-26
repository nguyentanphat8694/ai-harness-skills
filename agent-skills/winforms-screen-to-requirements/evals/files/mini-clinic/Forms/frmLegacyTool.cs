using System;
namespace MiniClinic
{
    // Old maintenance tool. Nothing opens it any more.
    public partial class frmLegacyTool : DevExpress.XtraEditors.XtraForm
    {
        private void btnFix_Click(object sender, EventArgs e) { ReceiptDal.RebuildIndex(); }
    }
}
