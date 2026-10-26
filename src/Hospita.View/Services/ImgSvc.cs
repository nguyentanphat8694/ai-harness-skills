
using System.Drawing;
using System.IO;

namespace Hospital.App.Services
{
    public class ImgSvc
    {
        public Image GetImgFromObImage(ObImage obj)
        {
            Image result;
            string path = obj.Path;
            if (path != "")
            {
                if (NTPUserSetting.DDLuuAnhSA != "")
                {
                    using (UNCAccessWithCredentials uNCAccessWithCredentials = new UNCAccessWithCredentials())
                    {
                        
                        if (true)//uNCAccessWithCredentials.NetUseWithCredentials(NTPUserSetting.DDLuuAnhSA, NTPUserSetting.PathServer_User, NTPUserSetting.PathServer_Domain, NTPUserSetting.PathServer_Password))
                        {
                            try
                            {
                                var networkLuuAnh = NTPUserSetting.NetworkLuuAnhSA;
                                path = !string.IsNullOrEmpty(networkLuuAnh) && path.Contains(NTPUserSetting.DDLuuAnhSA) ? path.Replace(NTPUserSetting.DDLuuAnhSA, networkLuuAnh) : path;
                                FileInfo fileInfo = new FileInfo(path);
                                if (fileInfo.Exists)
                                    return Image.FromFile(path);
                                else
                                {
                                    if (!string.IsNullOrEmpty(networkLuuAnh) && path.Contains(NTPUserSetting.DDLuuAnhSA))
                                    {
                                        var netWorkPath = path.Replace(NTPUserSetting.DDLuuAnhSA, networkLuuAnh);
                                        fileInfo = new FileInfo(netWorkPath);
                                        return fileInfo.Exists ? Image.FromFile(path) : null;
                                    }
                                    else
                                        return null;
                                }
                            }
                            catch
                            {
                            }
                        }
                    }
                }
                else
                {
                    try
                    {
                        FileInfo fileInfo = new FileInfo(path);
                        result = (fileInfo.Exists ? Image.FromFile(path) : null);
                        return result;
                    }
                    catch
                    {
                    }
                }
            }
            return null;
        }
    }
}
