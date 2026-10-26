partial class frmMain
{
    private void InitializeComponent()
    {
        this.btnReceipt = new DevExpress.XtraBars.BarButtonItem();
        this.btnDrug = new DevExpress.XtraBars.BarButtonItem();
        this.btnTax = new DevExpress.XtraBars.BarButtonItem();
        this.btnReceipt.Caption = "PHIẾU THU";
        this.btnReceipt.ItemClick += new DevExpress.XtraBars.ItemClickEventHandler(this.btnReceipt_ItemClick);
        this.btnDrug.Caption = "DANH MỤC THUỐC";
        this.btnDrug.ItemClick += new DevExpress.XtraBars.ItemClickEventHandler(this.btnDrug_ItemClick);
        this.btnTax.Caption = "BÁO CÁO THUẾ";
        this.btnTax.ItemClick += new DevExpress.XtraBars.ItemClickEventHandler(this.btnTax_ItemClick);
        this.Text = "PHẦN MỀM PHÒNG KHÁM MẪU";
    }
}
