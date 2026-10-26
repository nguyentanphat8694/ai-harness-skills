using System.Data.SqlClient;
namespace MiniClinic
{
    public class ReceiptDal
    {
        public static double NextId()
        {
            var r = Db.Query("Select Max(Id) From tb_Receipt");
            return r.Read() && !r.IsDBNull(0) ? r.GetDouble(0) + 1 : 1;
        }
        public static void Insert(Receipt r)
        {
            var c = new SqlCommand("INSERT INTO tb_Receipt (Id, PatientCode, Discount, Status) VALUES(@Id, @P, @D, @S)");
            Db.Exec(c);
        }
        public static void AttachLine(double receiptId, ReceiptLine l)
        {
            var c = new SqlCommand("UPDATE tb_Line SET ReceiptId=@R WHERE Code=@C");
            Db.Exec(c);
        }
        public static double SumBetween(System.DateTime a, System.DateTime b)
        {
            var c = new SqlCommand("SELECT SUM(Discount) FROM tb_Receipt WHERE Status='Paid'");
            return 0;
        }
        public static void RebuildIndex() { Db.Exec(new SqlCommand("EXEC sp_RebuildIndexes")); }
    }
}
