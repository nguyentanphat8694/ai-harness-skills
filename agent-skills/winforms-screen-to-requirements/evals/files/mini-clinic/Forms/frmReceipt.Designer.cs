partial class frmReceipt
{
    private void InitializeComponent()
    {
        this.Text = "PHIẾU THU TIỀN";
        this.lblPatient.Text = "Mã bệnh nhân";
        this.lblTotal.Text = "Tổng tiền";
        this.lblDiscount.Text = "Giảm giá";
        this.lblPayable.Text = "Phải thu";
        this.lblTendered.Text = "Khách đưa";
        this.lblChange.Text = "Tiền thối";
        this.txtTotal.Properties.ReadOnly = true;
        this.txtPayable.Properties.ReadOnly = true;
        this.txtChange.Properties.ReadOnly = true;
        this.btnSave.Text = "LƯU";
        this.btnPrint.Text = "IN PHIẾU";
        this.btnPrint.Enabled = false;
        this.mnuDeleteRow.Text = "Xóa dòng";
        this.txtDiscount.EditValueChanged += new System.EventHandler(this.txtDiscount_EditValueChanged);
        this.txtTendered.EditValueChanged += new System.EventHandler(this.txtTendered_EditValueChanged);
        this.btnSave.Click += new System.EventHandler(this.btnSave_Click);
        this.btnPrint.Click += new System.EventHandler(this.btnPrint_Click);
    }
}
