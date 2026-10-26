partial class frmTaxReport
{
    private void InitializeComponent()
    {
        this.dtFrom = new System.Windows.Forms.DateTimePicker();
        this.dtTo = new System.Windows.Forms.DateTimePicker();
        this.btnRun = new DevExpress.XtraEditors.SimpleButton();
        this.lblFrom.Text = "Từ ngày";
        this.lblTo.Text = "Đến ngày";
        this.lblTax.Text = "Thuế phải nộp";
        this.btnRun.Text = "TÍNH THUẾ";
        this.btnRun.Click += new System.EventHandler(this.btnRun_Click);
        this.Text = "BÁO CÁO THUẾ";
    }
}
