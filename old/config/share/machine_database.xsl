<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0">
  
  <xsl:output method="html"/>
  <xsl:template match="/">
    <html>
      <body bgcolor="#AF8FAF">
        <xsl:apply-templates select="machine_database/machines"/>
        <xsl:apply-templates select="machine_database/machine_types"/>
        <xsl:apply-templates select="machine_database/kernels"/>
      </body>
    </html>
  </xsl:template>
  
  <xsl:template match="machines">
    <h2>Machines</h2>
    <table border="6">
      <thead>
        <th>Name</th>
        <th>mtype</th>
        <th>kernel</th>
        <th>filesystem</th>
        <th>profile</th>
      </thead>
      <tbody>
        <xsl:for-each select="/machine_database/machines/machine">
          <xsl:apply-templates select="."/>
        </xsl:for-each>
      </tbody>
    </table>
  </xsl:template>
  
  <xsl:template match="machine_types">
    <h2>Machine Types</h2>
    <table border="6">
      <thead>
        <th>mtype</th>
        <th>diskname</th>
        <th>device</th>
      </thead>
      <tbody>
        <xsl:for-each select="/machine_database/machine_types/machine_type">
          <xsl:apply-templates select="."/>
        </xsl:for-each>
      </tbody>
    </table>
  </xsl:template>

  <xsl:template match="disks">
    <h2>Disks</h2>
    <table border="6">
      <thead>
        <th>diskname</th>
        <th>partition</th>
        <th>start</th>
        <th>size</th>
        <th>Id</th>
      </thead>
      <tbody>
        <xsl:for-each select="/machine_database/disks/diskname">
          <xsl:apply-templates select="."/>
        </xsl:for-each>
      </tbody>
    </table>
  </xsl:template>
  
  <xsl:template match="kernels">
    <h2>Kernels</h2>
    <table border="6">
      <thead>
        <th>kernel</th>
      </thead>
      <tbody>
        <xsl:for-each select="/machine_database/kernels/kernel">
          <xsl:apply-templates select="."/>
        </xsl:for-each>
      </tbody>
    </table>
  </xsl:template>
  
  <xsl:template match="profile">
    <h1>Profile: <xsl:value-of select="@name"/></h1>
    <h3> Suite: <xsl:value-of select="@suite"/></h3>
  </xsl:template>
  
  <xsl:template match="machine">
    <tr>
      <td><xsl:value-of select="."/></td>
      <td><xsl:value-of select="@machine_type"/></td>
      <td><xsl:value-of select="@kernel"/></td>
      <td><xsl:value-of select="@filesystem"/></td>
      <td><xsl:value-of select="@profile"/></td>
    </tr>
  </xsl:template>
  
  <xsl:template match="kernel">
    <tr>
      <td><xsl:value-of select="."/></td>
    </tr>
  </xsl:template>
  
  <xsl:template match="machine_type">
    <tr>
      <td><xsl:value-of select="@name"/></td>
      <td><xsl:value-of select="machine_disk/@diskname"/></td>
      <td><xsl:value-of select="machine_disk/@device"/></td>
    </tr>
  </xsl:template>
  
  <xsl:template match="diskname">
    <xsl:for-each select="partition">
    <tr>
      <td><xsl:value-of select="../@name"/></td>
      <xsl:apply-templates select="."/>
    </tr>
  </xsl:for-each>
  </xsl:template>
  
  <xsl:template match="partition">
      <td><xsl:value-of select="@partition"/></td>
      <td><xsl:value-of select="@start"/></td>
      <td><xsl:value-of select="@size"/></td>
      <td><xsl:value-of select="@Id"/></td>
  </xsl:template>
  
</xsl:stylesheet>
