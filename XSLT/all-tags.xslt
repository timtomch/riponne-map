<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="text"/>

  <xsl:variable name="newline">
<xsl:text>
</xsl:text>
  </xsl:variable>

  <xsl:key name="tags" match="*" use="name()"/>

  <xsl:template match="/">
    <xsl:value-of select="$newline"/>
    <xsl:text>Tags MARC utilisés</xsl:text>
    <xsl:value-of select="$newline"/>
    <xsl:value-of select="$newline"/>
    <xsl:for-each 
      select="//*[generate-id(.)=generate-id(key('tags',name())[1])]">
      <xsl:sort select="name()"/>
      <xsl:for-each select="key('tags', name())">
        <xsl:if test="position()=1">
          <xsl:text>Element </xsl:text>
          <xsl:value-of select="name()"/>
          <xsl:text> occurs </xsl:text>
          <xsl:value-of select="count(//*[name()=name(current())])"/>
          <xsl:text> times.</xsl:text>
          <xsl:value-of select="$newline"/>
        </xsl:if>
      </xsl:for-each>
    </xsl:for-each>
    <xsl:value-of select="$newline"/>
    <xsl:text>There are </xsl:text>
    <xsl:value-of select="count(//*)"/>
    <xsl:text> elements in all.</xsl:text>
    <xsl:value-of select="$newline"/>
  </xsl:template>
    
</xsl:stylesheet>