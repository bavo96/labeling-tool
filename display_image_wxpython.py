import os
import wx
import io
import csv
import sys
import time
import requests

def read_csv(dir):
    images = []
    with open(dir) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0: # Header
                line_count += 1
            else:
                images.append(row)
                line_count += 1
    return images

def save_csv(file_name, images):
    with open(file_name, mode='w') as file:
        file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow(['', 'request_id','bot_prediction', 'url', 'local_dir', 'true/false'])
        file_writer.writerows(images)

count = 0
bot_true = 0
bot_false = 0
#input_csv = "bot_detection_results_production.csv"
input_csv = "bot_pred_prod_14_1-5_2.csv"
output_csv = "out.csv"
images = read_csv(input_csv)

print("Total images:", len(images))

while(1):
    if images[count][5] == "":
        print("Number of images that have been labeled:", count)
        break
    elif images[count][5] == "TRUE":
        bot_true += 1
    elif images[count][5] == "FALSE":
        bot_false += 1
    count += 1

print("Enter the range of data you want to label!")
print("From:", count)
upper_bound = int(input("To: "))
while upper_bound < count:
    upper_bound = int(input("upper_bound < lower_bound, try again. To: "))
print("Start labeling at Image", count)

class PanelImage(wx.Panel):
    def __init__(self, parent, id, image_url):
        # create the panel
        wx.Panel.__init__(self, parent, id)
        self.parent = parent
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.bitmap = None
        try:
            # pick a .jpg file you have in the working folder
            # --- Download and read images ---
            #print(image_url)
            #response = requests.get(image_url)
            #sbuf = io.BytesIO(response.content)
            #img = wx.Image(sbuf).Scale(680, 550, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()  

            # --- Read images from local ---
            jpg = wx.Image(image_url, wx.BITMAP_TYPE_ANY).Scale(680, 550, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
            self.bitmap = wx.Bitmap(jpg)
            self.Refresh()

        except IOError:
            print("Image file %s not found" % image_url)
            #raise SystemExit

    def OnPaint(self, evt):
        if self.bitmap != None:
            dc = wx.BufferedPaintDC(self)
            dc.Clear()
            dc.DrawBitmap(self.bitmap, 0,0)
        else:
            pass

    def changeBitmapWorker(self, image_url):
        try:
            # pick a .jpg file you have in the working folder
            # --- Download and read images ---
            #print(image_url)
            #response = requests.get(image_url)
            #sbuf = io.BytesIO(response.content)
            #img = wx.Image(sbuf).Scale(680, 550, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()  

            # --- Read images from local ---
            jpg = wx.Image(image_url, wx.BITMAP_TYPE_ANY).Scale(680, 550, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
            self.bitmap = wx.Bitmap(jpg)
            self.Refresh()

        except IOError:
            print("Image file %s not found" % image_url)
            #raise SystemExit

class PanelButton(wx.Panel):
    """ class Panel1 creates a panel with an image on it, inherits wx.Panel """
    def __init__(self, parent, id, top_panel, text):
        # create the panel
        global count, images, bot_true, bot_false

        wx.Panel.__init__(self, parent, id, size = (100, 100))
        self.SetBackgroundColour("white")

        # Bot text
        self.font = wx.Font(20, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_SLANT, wx.FONTWEIGHT_BOLD)
        self.bot_label = wx.StaticText(self, label=text, size = (150, 50), style = wx.ALIGN_CENTRE|wx.ST_ELLIPSIZE_END)
        self.bot_label.SetFont(self.font)
        self.bot_label.SetBackgroundColour("yellow")
        
        # Info text
        info_text = "Current image: {}/{}\nBot true: {}\nBot false: {}".format(count, len(images), bot_true, bot_false)
        self.info = wx.StaticText(self, label=info_text, size = (200, 100), style = wx.ALIGN_CENTRE|wx.ST_ELLIPSIZE_END)
        self.info.SetBackgroundColour("green")

        # Set sizer
        sizer_v = wx.BoxSizer(wx.VERTICAL)
        sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        sizer_h.Add(self.info, 1, wx.CENTER)
        sizer_v.Add(sizer_h, 1, wx.CENTER)
        self.SetSizer(sizer_v)
        
        sizer_v = wx.BoxSizer(wx.VERTICAL)
        sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        sizer_h.Add(self.bot_label, 1, wx.CENTER)
        sizer_v.Add(sizer_h, 1, wx.CENTER)
        self.SetSizer(sizer_v)

        self.top_panel = top_panel
        self.Bind(wx.EVT_CHAR, self.OnKeyDown)
        self.SetFocus()

    def OnKeyDown(self, event):
        global count, bot_false, bot_true
        keycode = event.GetKeyCode()
        if keycode == 113:
            print("Shutdown the program.")
            sys.exit()
        if count < len(images) and count < upper_bound:
            if keycode == wx.WXK_LEFT:
                print("Rejected!")
                images[count][5] = "FALSE"
                bot_false += 1
                count += 1
            elif keycode == wx.WXK_RIGHT:
                print("Approved!")
                images[count][5] = "TRUE"
                bot_true += 1
                count += 1
            elif keycode == 98:
                print("Withdraw!")
                count -=1
                if images[count][5] == "TRUE":
                    bot_true -= 1
                elif images[count][5] == "FALSE":
                    bot_false -= 1
                self.top_panel.changeBitmapWorker(images[count][4])
                self.bot_label.SetLabel(images[count][2])
                info_text = "Current image: {}/{}\nBot true: {}\nBot false: {}".format(count, len(images), bot_true, bot_false)
                self.info.SetLabel(info_text)
            elif keycode == 115:
                print("Save results to {}.".format(output_csv))
                save_csv(output_csv, images)
            
            if count < len(images) and count < upper_bound:
                self.top_panel.changeBitmapWorker(images[count][4])
                self.bot_label.SetLabel(images[count][2])
                #self.bot_label.Layout()
                info_text = "Current image: {}/{}\nBot true: {}\nBot false: {}".format(count, len(images), bot_true, bot_false)
                self.info.SetLabel(info_text)
            else:
                if self.top_panel:
                    self.top_panel.Destroy()
                self.bot_label.SetLabel("NONE")
                self.bot_label.Layout()
                info_text = "Current image: {}/{}\nBot true: {}\nBot false: {}".format(count, len(images), bot_true, bot_false)
                self.info.SetLabel(info_text)
                print("Save results to {}.".format(output_csv))
                save_csv(output_csv, images)
        else:
            print("No more images.")

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        global count
        wx.Frame.__init__(self, parent, id, title,size=(700, 700))
        Panel = wx.Panel(self)

        top_panel = PanelImage(Panel, -1, images[count][4])
        bottom_panel = PanelButton(Panel, -1, top_panel, images[count][2])

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(top_panel,1,wx.EXPAND|wx.ALL,border=10)
        sizer.Add(bottom_panel,0,wx.EXPAND|wx.ALL,border=10)

        Panel.SetSizer(sizer)        
        self.Centre()
        
        #wx.EVT_CLOSE(self, self.OnCloseWindow)
        
    def OnCloseWindow(self, event):
        self.Destroy()

class MyApp(wx.App):
     def OnInit(self):
         frame = MyFrame(None, -1, '"An image on a panel"')
         frame.Show(True)
         return True
app = MyApp(0)
app.MainLoop()




