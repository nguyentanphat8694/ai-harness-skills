partial class frmDrug
{
    private void InitializeComponent()
    {
        this.txtName = new DevExpress.XtraEditors.TextEdit();
        this.txtPrice = new DevExpress.XtraEditors.TextEdit();
        this.btnAdd = new DevExpress.XtraEditors.SimpleButton();
        this.lblName.Text = "Tên thuốc";
        this.lblPrice.Text = "Đơn giá";
        this.btnAdd.Text = "THÊM";
        this.btnAdd.Click += new System.EventHandler(this.btnAdd_Click);
        this.Text = "DANH MỤC THUỐC";
    }
}
