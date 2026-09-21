﻿Add-Type -AssemblyName System.Drawing
$base = "d:\新建文件夹\I3DM\results_showcase"
$scenes = @("005dd9a58df1ba3c","01aaf4ebb084dc16","04e4c841b349bf5c")
$segs = @("seg1","seg3","seg6")

foreach ($s in $scenes) {
    [int]$W = 640
    [int]$H = 352
    [int]$labelH = 36
    [int]$rows = 3
    [int]$totalW = $W * 2
    [int]$totalH = $H * $rows + $labelH * ($rows + 1)

    $bmp = New-Object System.Drawing.Bitmap($totalW, $totalH)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.Clear([System.Drawing.Color]::White)
    $font = New-Object System.Drawing.Font("Arial", 16, [System.Drawing.FontStyle]::Bold)
    $brush = [System.Drawing.Brushes]::Black
    $sf = New-Object System.Drawing.StringFormat
    $sf.Alignment = [System.Drawing.StringAlignment]::Center

    for ($r = 0; $r -lt $rows; $r++) {
        [int]$y0 = $labelH + $r * ($H + $labelH)
        $rectLabel = New-Object System.Drawing.RectangleF(0, $y0, $totalW, $labelH)
        $g.DrawString("Segment $($r+1)  (frame 38)", $font, $brush, $rectLabel, $sf)
        $genPath = Join-Path $base "$s\gen_$($segs[$r])_f38.png"
        $gtPath = Join-Path $base "$s\gt_$($segs[$r])_f38.png"
        $gen = [System.Drawing.Image]::FromFile($genPath)
        $gt = [System.Drawing.Image]::FromFile($gtPath)
        $g.DrawImage($gen, 0, ($y0 + $labelH), $W, $H)
        $g.DrawImage($gt, $W, ($y0 + $labelH), $W, $H)
        $gen.Dispose()
        $gt.Dispose()
    }
    [int]$yEnd = $H * $rows + $labelH * $rows
    $rectEnd = New-Object System.Drawing.RectangleF(0, $yEnd, $totalW, $labelH)
    $g.DrawString("I3DM Generated (left)  vs  Ground Truth (right)", $font, $brush, $rectEnd, $sf)
    $g.Dispose()

    $out = Join-Path $base "$s\compare_grid.jpg"
    $enc = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq "image/jpeg" }
    $ep = New-Object System.Drawing.Imaging.EncoderParameters(1)
    $ep.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter([System.Drawing.Imaging.Encoder]::Quality, [long]88)
    $bmp.Save($out, $enc, $ep)
    $bmp.Dispose()
    $size = (Get-Item $out).Length
    Write-Output "$s -> compare_grid.jpg ($([math]::Round($size/1KB)) KB)"
}
