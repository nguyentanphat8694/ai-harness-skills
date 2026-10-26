using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;
namespace MiniClinic
{
    public partial class frmReceipt : DevExpress.XtraEditors.XtraForm
    {
        List<ReceiptLine> lines = new List<ReceiptLine>();

        void Recalc()
        {
            double total = lines.Sum(l => l.Qty * l.Price);
            txtTotal.Text = total.ToString("n0");
            double payable = total - Parse(txtDiscount.Text);
            txtPayable.Text = payable.ToString("n0");
            txtChange.Text = (Parse(txtTendered.Text) - payable).ToString("n0");
        }

        static double Parse(string s)
        {
            double d;
            return double.TryParse(s, out d) ? d : 0;
        }

        bool Validate()
        {
            if (string.IsNullOrEmpty(txtPatient.Text)) { MessageBox.Show("Vui lòng chọn bệnh nhân"); return false; }
            if (lines.Count == 0) { MessageBox.Show("Không có dịch vụ để thu"); return false; }
            foreach (var l in lines)
            {
                if (l.Type == eItemType.Drug && StockDal.GetStock(l.Code) < l.Qty)
                {
                    MessageBox.Show("Không đủ tồn kho: " + l.Code);
                    return false;
                }
            }
            return true;
        }

        private void btnSave_Click(object sender, EventArgs e)
        {
            if (!Validate()) return;
            var r = new Receipt { PatientCode = txtPatient.Text, Discount = Parse(txtDiscount.Text), Status = eStatus.Paid.ToString() };
            r.Id = ReceiptDal.NextId();
            ReceiptDal.Insert(r);
            foreach (var l in lines) ReceiptDal.AttachLine(r.Id, l);
            MessageBox.Show("Đã lưu phiếu thu");
            btnPrint.Enabled = true;
        }

        private void btnPrint_Click(object sender, EventArgs e)
        {
            new frmReceiptPrint().ShowDialog();
        }

        private void txtDiscount_EditValueChanged(object sender, EventArgs e) { Recalc(); }
        private void txtTendered_EditValueChanged(object sender, EventArgs e) { Recalc(); }
    }
}
