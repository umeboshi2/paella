<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0">
  
  <xsl:output method="html"/>
  <xsl:template match="/">
    <html>
      <body bgcolor="#AF8FAF">
        <xsl:apply-templates select="profile"/>
        <xsl:apply-templates select="profile/traits"/>
        <xsl:apply-templates select="profile/families"/>
        <xsl:apply-templates select="profile/environ"/>
      </body>
    </html>
  </xsl:template>
  <xsl:template match="profile">
    <h1>Profile: <xsl:value-of select="@name"/></h1>
    <h3> Suite: <xsl:value-of select="@suite"/></h3>
  </xsl:template>
  <xsl:template match="profile/traits">
    <table border="6">
      <thead><th>Trait</th><th>Order</th></thead>
      <tbody>
        <xsl:for-each select="//trait">
          <xsl:apply-templates select="."/>
        </xsl:for-each>
      </tbody>
    </table>
  </xsl:template>
  <xsl:template match="profile/families">
    <h2>Families</h2>
    <table border="6"><thead><th>Family</th></thead>
    <tbody>
      <xsl:for-each select="//family">
        <xsl:apply-templates select="."/>
      </xsl:for-each>
    </tbody>
</table>
  </xsl:template>
   <xsl:template match="profile/environ">
     <h2>Environment</h2>
    <table border="6">
      <thead><th>Trait</th><th>Name</th><th>Value</th></thead>
      <tbody>
        <xsl:for-each select="//profile_variable">
          <xsl:apply-templates select="."/>
        </xsl:for-each>
      </tbody>
    </table>
  </xsl:template>
  <xsl:template match="trait">
    <tr>
      <td><xsl:value-of select="."/></td>
      <td><xsl:value-of select="@ord"/></td>
    </tr>
  </xsl:template>
  <xsl:template match="family">
    <tr>
      <td><xsl:value-of select="."/></td>
    </tr>
  </xsl:template>
  <xsl:template match="profile_variable">
    <tr>
      <td>
        <xsl:value-of select="@trait"/>
      </td>
      <td>
        <xsl:value-of select="@name"/>
      </td>
      <td>
        <xsl:value-of select="."/>
      </td>
    </tr>
  </xsl:template>
  
</xsl:stylesheet>
