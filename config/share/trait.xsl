<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <xsl:output method="html"/>

  <xsl:template match="/">
    <html>
      <body bgcolor="#FFFFFF">
        <xsl:apply-templates/>
      </body>
    </html>
  </xsl:template>
  <xsl:template match="parent">
    <tr>
      <td><xsl:value-of select="."/></td>
    </tr>
  </xsl:template>
  <xsl:template match="package">
    <tr>
      <td><xsl:value-of select="."/></td>
      <td><xsl:value-of select="@action"/></td>
    </tr>
  </xsl:template>
  <xsl:template match="environ">
    <h2>Variables</h2>
  </xsl:template>
</xsl:stylesheet>
