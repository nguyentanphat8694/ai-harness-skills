using System;
namespace MiniClinic
{
    public partial class frmTaxReport : DevExpress.XtraEditors.XtraForm
    {
        private void btnRun_Click(object sender, EventArgs e)
        {
            double revenue = ReceiptDal.SumBetween(dtFrom.Value, dtTo.Value);
            lblTax.Text = Missing.Core.TaxCalc.Compute(revenue).ToString("n0");
        }
    }
}
