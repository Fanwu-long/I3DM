﻿Add-Type -AssemblyName System.Drawing
$base = "d:\新建文件夹\I3DM\results_showcase"

# parse loss data
$data = @()
Get-Content (Join-Path $base "loss_dump.txt") | ForEach-Object {
    $p = $_.Trim() -split '\s+'
    if ($p.Count -eq 2) {
        $step = 0; $val = 0.0
        if ([int]::TryParse($p[0], [ref]$step) -and [double]::TryParse($p[1], [ref]$val)) {
            $data += [PSCustomObject]@{ Step = $step; Loss = $val }
        }
    }
}
Write-Output "parsed $($data.Count) points, min=$([math]::Round(($data | Measure-Object Loss -Minimum).Minimum,5)), max=$([math]::Round(($data | Measure-Object Loss -Maximum).Maximum,5))"

# moving average (window 5) for trend line
$ma = @()
for ($i = 0; $i -lt $data.Count; $i++) {
    $lo = [Math]::Max(0, $i - 2); $hi = [Math]::Min($data.Count - 1, $i + 2)
    $win = $data[$lo..$hi]
    $ma += [PSCustomObject]@{ Step = $data[$i].Step; Loss = ($win | Measure-Object Loss -Average).Average }
}

[int]$W = 1000; [int]$H = 560
[int]$mL = 90; [int]$mR = 40; [int]$mT = 60; [int]$mB = 70
[int]$pw = $W - $mL - $mR; [int]$ph = $H - $mT - $mB

$bmp = New-Object System.Drawing.Bitmap($W, $H)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.Clear([System.Drawing.Color]::White)

$fontTitle = New-Object System.Drawing.Font("Arial", 16, [System.Drawing.FontStyle]::Bold)
$fontAxis = New-Object System.Drawing.Font("Arial", 12)
$fontSmall = New-Object System.Drawing.Font("Arial", 10)
$brushBlack = [System.Drawing.Brushes]::Black
$brushGray = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Gray)

$xMin = 0; $xMax = 210; $yMin = 0.0; $yMax = 0.30
function X($step) { return [int]($mL + ($step - $xMin) / ($xMax - $xMin) * $pw) }
function Y($val) { return [int]($mT + (1 - ($val - $yMin) / ($yMax - $yMin)) * $ph) }

# grid + y labels
$penGrid = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(220, 220, 220), 1)
for ($v = 0.0; $v -le 0.301; $v += 0.05) {
    $yy = Y $v
    $g.DrawLine($penGrid, $mL, $yy, ($mL + $pw), $yy)
    $g.DrawString(("{0:F2}" -f $v), $fontSmall, $brushGray, ($mL - 48), ($yy - 8))
}
for ($s = 0; $s -le 200; $s += 25) {
    $xx = X $s
    $g.DrawLine($penGrid, $xx, $mT, $xx, ($mT + $ph))
    $g.DrawString("$s", $fontSmall, $brushGray, ($xx - 10), ($mT + $ph + 8))
}
# axes
$penAxis = New-Object System.Drawing.Pen([System.Drawing.Color]::Black, 2)
$g.DrawLine($penAxis, $mL, $mT, $mL, ($mT + $ph))
$g.DrawLine($penAxis, $mL, ($mT + $ph), ($mL + $pw), ($mT + $ph))

# raw loss line (blue, thin)
$penRaw = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(70, 130, 230), 2)
for ($i = 0; $i -lt ($data.Count - 1); $i++) {
    $g.DrawLine($penRaw, (X $data[$i].Step), (Y $data[$i].Loss), (X $data[$i+1].Step), (Y $data[$i+1].Loss))
}
$brushPt = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(70, 130, 230))
foreach ($d in $data) {
    $g.FillEllipse($brushPt, ((X $d.Step) - 4), ((Y $d.Loss) - 4), 8, 8)
}

# moving average line (red, thick)
$penMA = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(210, 60, 60), 3)
for ($i = 0; $i -lt ($ma.Count - 1); $i++) {
    $g.DrawLine($penMA, (X $ma[$i].Step), (Y $ma[$i].Loss), (X $ma[$i+1].Step), (Y $ma[$i+1].Loss))
}

# title and axis labels
$g.DrawString("I3DM Smoke Training Loss (200 steps, LoRA rank 1024)", $fontTitle, $brushBlack, ($mL + 130), 15)
$sf = New-Object System.Drawing.StringFormat
$sf.Alignment = [System.Drawing.StringAlignment]::Center
$g.DrawString("Training Step", $fontAxis, $brushBlack, (New-Object System.Drawing.RectangleF($mL, ($H - 40), $pw, 30)), $sf)
$g.RotateTransform(-90)
$g.DrawString("Training Loss", $fontAxis, $brushBlack, (-($mT + $ph) - 60), 30)
$g.RotateTransform(90)

# legend
$g.FillRectangle($brushPt, 700, 22, 14, 14)
$g.DrawString("loss (per 10 steps)", $fontSmall, $brushBlack, 720, 20)
$g.DrawLine($penMA, 860, 29, 890, 29)
$g.DrawString("moving avg (5)", $fontSmall, $brushBlack, 895, 20)

$g.Dispose()
$out = Join-Path $base "training_loss_curve.png"
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
Write-Output "saved: $out ($([math]::Round((Get-Item $out).Length/1KB)) KB)"
