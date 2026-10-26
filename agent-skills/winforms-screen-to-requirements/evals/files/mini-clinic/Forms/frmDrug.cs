using System;
namespace MiniClinic
{
    public partial class frmDrug : DevExpress.XtraEditors.XtraForm
    {
        private void btnAdd_Click(object sender, EventArgs e)
        {
            if (string.IsNullOrEmpty(txtName.Text)) { MessageBox.Show("Nhập tên thuốc"); return; }
            DrugDal.Insert(txtName.Text, Parse(txtPrice.Text));
        }
    }
}
