using SHPT.Utils.Capture;
using System;

namespace Hospital.App.Sieu_Am
{
    public class UNewCapture : UCapture
    {
        public UNewCapture()
        {
            picSrc.SelectionChanged += onSelectionChange;
        }

        private void onSelectionChange(object sender, EventArgs e)
        {
            throw new NotImplementedException();
        }
    }
}
