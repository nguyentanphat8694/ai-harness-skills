namespace Hospital.App
{
    public class CaptureParams
    {
        public bool IsAll { get; set; }
        public int X { get; set; }
        public int Y { get; set; }
        public int Width { get; set; }
        public int Height { get; set; }
        public CaptureParams(bool isAll, int x, int y, int width, int height)
        {
            IsAll = isAll;
            X = x;
            Y = y;
            Width = width;
            Height = height;
        }
    }
}
